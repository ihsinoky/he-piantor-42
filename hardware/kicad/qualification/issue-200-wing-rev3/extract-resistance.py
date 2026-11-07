"""Read-only DC FEM on Rev.3 actual filled copper, pads, tracks and via barrels.
Reuses Issue196 triangular sheet assembly and KCL solver, generalized to 2 layers
and distributed Wing loads. Not a physical measurement or fabrication bound.
"""
from pathlib import Path
import sys,json,hashlib,math
sys.path[:0]=['/home/hatch/workspace/projects/he-piantor-42/.issue175-runtime/python','/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/venv/lib/python3.12/site-packages']
import pcbnew as p,numpy as np,triangle
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import splu
from scipy.sparse.csgraph import connected_components
from shapely.geometry import Point,Polygon,LineString,box
from shapely.ops import unary_union
from shapely import contains_xy,set_precision
from verify import polys,padgeom,xy
E=Path(__file__).resolve().parent
mm=p.ToMM
def sheet_elements(pts,area2):
 bb=np.stack([pts[:,1,1]-pts[:,2,1],pts[:,2,1]-pts[:,0,1],pts[:,0,1]-pts[:,1,1]],axis=1)
 cc=np.stack([pts[:,2,0]-pts[:,1,0],pts[:,0,0]-pts[:,2,0],pts[:,1,0]-pts[:,0,0]],axis=1)
 return (bb[:,:,None]*bb[:,None,:]+cc[:,:,None]*cc[:,None,:])/(2*area2[:,None,None])*35e-6/1.7241e-8

def mesh(poly,area,seeds):
 # 2um boundary simplification is recorded, far below 0.10mm routing floor.
 poly=set_precision(poly, .000001).simplify(.002,preserve_topology=True)
 vs=[];seg=[];holes=[]
 for line in [poly.exterior]+list(poly.interiors):
  coords=list(line.coords)[:-1];start=len(vs);vs.extend(coords);seg.extend((start+i,start+(i+1)%len(coords)) for i in range(len(coords)))
 for hole in poly.interiors:holes.append(list(Polygon(hole).representative_point().coords)[0])
 seen={tuple(q) for q in vs}
 for q in seeds:
  q=tuple(round(x,6) for x in q)
  if tuple(q) not in seen and poly.contains(Point(q)):vs.append(q);seen.add(tuple(q))
 origin=np.min(np.array(vs),axis=0)
 d=dict(vertices=np.array(vs)-origin,segments=np.array(seg))
 if holes:d['holes']=np.array(holes)-origin
 out=triangle.triangulate(d,'pq20a'+str(area)+'Q');v=out['vertices']+origin;tri=out['triangles'];return v,tri

def assemble(area,factor):
 shapes={l:[] for l in layers};padshapes={};barrels=[]
 for z in b.Zones():
  if not z.GetIsRuleArea() and z.GetNetname()==net:
   for l in layers:
    if z.IsOnLayer(l):shapes[l].append(polys(z.GetFilledPolysList(l)))
 for a in pads:
  g=padgeom(native[a['uuid']],next(l for l in layers if native[a['uuid']].IsOnLayer(l)));padshapes[a['ref']+'.'+a['number']+'@'+a['uuid']]=g
  drill=native[a['uuid']].GetDrillSize()
  if drill.x:
   assert drill.x==drill.y,'slotted PTH needs a capsule model'
   h=Point(a['position']).buffer(mm(drill.x)/2,quad_segs=128);g=g.difference(h)
   barrels.append(dict(id=a['uuid'],position=a['position'],outer=g,drill=mm(drill.x),layers=[l for l in layers if native[a['uuid']].IsOnLayer(l)]))
  for l in layers:
   if native[a['uuid']].IsOnLayer(l):shapes[l].append(g)
 for t in snap['tracks']:
  if t['net']==net and t['kind']=='track':shapes[t['layer']].append(LineString([t['start'],t['end']]).buffer(t['width']*factor/2,quad_segs=32))
 for v in vias:
  pos=xy(v.GetPosition());outer=Point(pos).buffer(mm(v.GetWidth(p.F_Cu))/2,quad_segs=32).difference(Point(pos).buffer(mm(v.GetDrillValue())/2,quad_segs=32))
  ls=[l for l in layers if v.IsOnLayer(l)];barrels.append(dict(id=v.m_Uuid.AsString(),position=pos,outer=outer,drill=mm(v.GetDrillValue()),layers=ls))
  for l in ls:shapes[l].append(outer)
 seeds=[]
 for barrel in barrels:
  x,y=barrel['position'];outer=barrel['outer'];radius=(barrel['drill']/2+min(outer.bounds[2]-x,outer.bounds[3]-y))/2
  seeds.extend((x+radius*math.cos(a*math.pi/4),y+radius*math.sin(a*math.pi/4)) for a in range(8))
 seeds.extend(tuple(a['position']) for a in pads)
 I=[];J=[];G=[];vertices={};N=0;meshstats={}
 def add(a,b,g):
  if a==b:return
  I.extend([a,a,b,b]);J.extend([a,b,a,b]);G.extend([g,-g,-g,g])
 for l in layers:
  geom=unary_union(shapes[l]);parts=list(geom.geoms) if geom.geom_type=='MultiPolygon' else [geom];vlist=[];counts=[]
  for poly in parts:
   if poly.area<1e-8:continue
   v,tr=mesh(poly,area,seeds);idx=tr+N;pts=v[tr];area2=np.abs((pts[:,1,0]-pts[:,0,0])*(pts[:,2,1]-pts[:,0,1])-(pts[:,1,1]-pts[:,0,1])*(pts[:,2,0]-pts[:,0,0]));assert np.min(area2)>0
   local=sheet_elements(pts,area2)
   for a in range(3):
    for d in range(3):
     I.extend(idx[:,a]);J.extend(idx[:,d]);G.extend(local[:,a,d])
   vlist.append((v,np.arange(N,N+len(v))));N+=len(v);counts.append(len(tr))
  vertices[l]=(np.vstack([a for a,_ in vlist]),np.concatenate([a for _,a in vlist]));meshstats[b.GetLayerName(l)]=dict(nodes=len(vertices[l][0]),triangles=sum(counts),area_mm2=geom.area)
 def contact(l,shape):
  v,ids=vertices[l];xmin,ymin,xmax,ymax=shape.bounds;mask=(v[:,0]>=xmin-.003)&(v[:,0]<=xmax+.003)&(v[:,1]>=ymin-.003)&(v[:,1]<=ymax+.003);cand=np.flatnonzero(mask);hit=cand[contains_xy(shape.buffer(.003),v[cand,0],v[cand,1])];assert len(hit)>0,('No mesh contact',b.GetLayerName(l),shape.bounds)
  return ids[hit]
 for barrel in barrels:
  hubs=[]
  for l in barrel['layers']:
   ids=contact(l,barrel['outer']);hub=N;N+=1
   for a in ids:add(int(a),hub,1e6)
   hubs.append((layers.index(l),hub))
  for (li,a),(lj,d) in zip(hubs,hubs[1:]):
   resistance=1.7241e-8*(zmm[lj]-zmm[li])*1e-3/(math.pi*barrel['drill']*1e-3*20e-6);add(a,d,1/resistance)
 terminals={}
 for a in pads:
  key=a['ref']+'.'+a['number'];hub=N;N+=1;terminals.setdefault(key,[]).append(hub)
  shape=padshapes[key+'@'+a['uuid']]
  # Only F.Cu terminal contact. PTHs reach other layers through explicit barrel.
  ids=contact(next(l for l in layers if native[a['uuid']].IsOnLayer(l)),shape)
  for i in ids:add(int(i),hub,1e6)
 K=coo_matrix((G,(I,J)),shape=(N,N)).tocsc()
 return K,terminals,meshstats

def solve(K,terms,source,loads):
 src=np.array(sorted({i for key in source for i in terms[key]}),dtype=int);_,labels=connected_components(K,directed=False);assert len(set(labels[src]))==1
 reach=np.flatnonzero(labels==labels[src[0]]);unknown=np.setdiff1d(reach,src);idx={v:i for i,v in enumerate(unknown)}
 rhs=np.zeros((len(unknown),len(loads)))
 for j,load in enumerate(loads):
  for key,current in load.items():
   for n in terms[key]:
    assert labels[n]==labels[src[0]],('Terminal disconnected',key)
    if n in idx:rhs[idx[n],j]+=current/len(terms[key])
 mat=K[unknown,:][:,unknown];lu=splu(mat);v=lu.solve(rhs)
 # Long-double residual / double LU iterative refinement avoids cancellation
 # in 1uOhm pad contact rows while retaining the original 1uA KCL criterion.
 extended=mat.astype(np.longdouble)
 for refinement in range(4):
  residual=rhs.astype(np.longdouble)-extended@v.astype(np.longdouble)
  if np.max(np.abs(residual))<1e-8:break
  v+=lu.solve(np.asarray(residual,dtype=float))
 res=float(np.max(np.abs(extended@v.astype(np.longdouble)-rhs)))
 assert res<1e-6,res
 out=[]
 for j,load in enumerate(loads):
  volt={k:float(np.mean([v[idx[n],j] if n in idx else 0 for n in ns])) for k,ns in terms.items() if all(labels[n]==labels[src[0]] for n in ns)}
  out.append(dict(load_A=load,terminal_voltage_V=volt,kcl_residual_A=res,reference_pads=source,nodes_solved=len(unknown)))
 return out

for name in sys.argv[1:]:
 w=E/name;b=p.LoadBoard(str(w/'main.kicad_pcb'));layers=[p.F_Cu,p.B_Cu];zmm=[0,1.2]
 native={a.m_Uuid.AsString():a for f in b.GetFootprints() for a in f.Pads()}
 snap=dict(tracks=[dict(kind='track',net=t.GetNetname(),layer=t.GetLayer(),width=mm(t.GetWidth()),start=xy(t.GetStart()),end=xy(t.GetEnd())) for t in b.GetTracks() if not isinstance(t,p.PCB_VIA)])
 rows=[]
 for net,pin in [('HALL_5V','1'),('GND','2')]:
  pads=[dict(ref=f.GetReference(),number=a.GetNumber(),uuid=a.m_Uuid.AsString(),position=xy(a.GetPosition())) for f in b.GetFootprints() for a in f.Pads() if a.GetNetname()==net]
  vias=[v for v in b.GetTracks() if isinstance(v,p.PCB_VIA) and v.GetNetname()==net]
  sources=[a['ref']+'.'+a['number'] for a in pads if a['ref']=='J_WING']
  # Original 21*5mA + 3*2.7uA proportions normalized to 127mA/Wing.
  loads={a['ref']+'.'+a['number']:(.005 if a['ref'].startswith('U_H') else .0000027)*.127/.1050081 for a in pads if a['ref'].startswith(('U_H','U_MUX'))}
  for area in [.06,.015]:
   for factor in [1.,.8]:
    K,terms,stats=assemble(area,factor);result=solve(K,terms,sources,[loads])[0]
    rows.append(dict(net=net,max_triangle_area_mm2=area,track_width_factor=factor,mesh=stats,result_at_20C=result));print(name,net,area,factor,flush=True)
    (w/'resistance-extraction.json').write_text(json.dumps(dict(board_sha256=hashlib.sha256((w/'main.kicad_pcb').read_bytes()).hexdigest(),rows=rows,assumptions=dict(copper_um=35,barrel_um=20,z_mm=zmm,temperature_coefficient=.00393,boundary_simplification_mm=.002,load_A=.127,GH_contact_model='one power, all six ground contacts ideal at board boundary'),limitations=['Numerical extraction from saved copper; no physical resistance measurement','Width factor applies to track widths, native filled-plane geometry unchanged, as Issue196. Copper/plating/etch minima and assembled resistance require acceptance','Pad and via landing equipotential approximations; no harness or contact resistance']),indent=2)+'\n')
