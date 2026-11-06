"""DC sheet finite elements from actual GND fill, tracks/pads and plated barrels.
Approximate extraction only: not manufactured minima or a sign-off bound.
"""
from common import *
sys.path[:0]=[str(T/'python'),str(B/'venv/lib/python3.12/site-packages')]
import pcbnew as p,numpy as np,triangle,importlib.util,math
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import splu
from scipy.sparse.csgraph import connected_components
from shapely.geometry import Point,Polygon,LineString,box
from shapely.ops import unary_union
from shapely import contains_xy
label=sys.argv[1];w=E/'inspection'/label;b=p.LoadBoard(str(w/'main.kicad_pcb'));snap=json.loads((w/'snapshot.json').read_text())
spec=importlib.util.spec_from_file_location('oracle',R/'hardware/kicad/qualification/issue-87-native-main-routing/check-main.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
layers=list(b.GetEnabledLayers().CuStack());zmm=[0,.2,1.,1.2] # documented assumed 1.2mm stack, not a guaranteed vendor stack
assert len(layers)==4
pads=[a for a in snap['pads'] if a['net']=='GND'];native={a.m_Uuid.AsString():a for f in b.GetFootprints() for a in f.Pads()};vias=[a for a in b.GetTracks() if isinstance(a,p.PCB_VIA) and a.GetNetname()=='GND']
mm=p.ToMM
xy=lambda v:(mm(v.x),mm(v.y))
def ring(l):return [xy(l.CPoint(i)) for i in range(l.PointCount())]
plane=[]
for zone in b.Zones():
 if zone.GetIsRuleArea() or zone.GetNetname()!='GND':continue
 poly=zone.GetFilledPolysList(p.In1_Cu)
 for i in range(poly.OutlineCount()):plane.append(Polygon(ring(poly.Outline(i)),[ring(poly.Hole(i,j)) for j in range(poly.HoleCount(i))]))
def mesh(poly,area,seeds):
 # 2um boundary simplification is recorded, far below 0.10mm routing floor.
 poly=poly.simplify(.002,preserve_topology=True)
 vs=[];seg=[];holes=[]
 for line in [poly.exterior]+list(poly.interiors):
  coords=list(line.coords)[:-1];start=len(vs);vs.extend(coords);seg.extend((start+i,start+(i+1)%len(coords)) for i in range(len(coords)))
 for hole in poly.interiors:holes.append(list(Polygon(hole).representative_point().coords)[0])
 seen={tuple(q) for q in vs}
 for q in seeds:
  if tuple(q) not in seen and poly.contains(Point(q)):vs.append(q);seen.add(tuple(q))
 d=dict(vertices=np.array(vs),segments=np.array(seg))
 if holes:d['holes']=np.array(holes)
 out=triangle.triangulate(d,'pq20a'+str(area)+'Q');v=out['vertices'];tri=out['triangles'];return v,tri

def assemble(area,factor):
 shapes={l:[] for l in layers};shapes[p.In1_Cu].extend(plane);padshapes={};barrels=[]
 for a in pads:
  g=m.shape(a);padshapes[a['ref']+'.'+a['number']+'@'+a['uuid']]=g
  drill=native[a['uuid']].GetDrillSize()
  if drill.x:
   h=m.capsule(a['position'],xy(drill));g=g.difference(h)
   barrels.append(dict(id=a['uuid'],position=a['position'],outer=g,drill=mm(drill.x),layers=[l for l in layers if native[a['uuid']].IsOnLayer(l)]))
  for l in layers:
   if native[a['uuid']].IsOnLayer(l):shapes[l].append(g)
 for t in snap['tracks']:
  if t['net']=='GND' and t['kind']=='track':shapes[t['layer']].append(LineString([t['start'],t['end']]).buffer(t['width']*factor/2,quad_segs=32))
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
  geom=unary_union(shapes[l]);polys=list(geom.geoms) if geom.geom_type=='MultiPolygon' else [geom];vlist=[];counts=[]
  for poly in polys:
   if poly.area<1e-8:continue
   v,tr=mesh(poly,area,seeds);idx=tr+N;pts=v[tr];area2=np.abs((pts[:,1,0]-pts[:,0,0])*(pts[:,2,1]-pts[:,0,1])-(pts[:,1,1]-pts[:,0,1])*(pts[:,2,0]-pts[:,0,0]));assert np.min(area2)>0
   bb=np.stack([pts[:,1,1]-pts[:,2,1],pts[:,2,1]-pts[:,0,1],pts[:,0,1]-pts[:,1,1]],axis=1)
   cc=np.stack([pts[:,2,0]-pts[:,1,0],pts[:,0,0]-pts[:,2,0],pts[:,1,0]-pts[:,0,0]],axis=1)
   for a in range(3):
    for d in range(3):
     g=(bb[:,a]*bb[:,d]+cc[:,a]*cc[:,d])/(2*area2)*35e-6/1.7241e-8
     I.extend(idx[:,a]);J.extend(idx[:,d]);G.extend(g)
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
  ids=contact(p.F_Cu,shape)
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
 mat=K[unknown,:][:,unknown];lu=splu(mat);v=lu.solve(rhs);res=float(np.max(np.abs(mat@v-rhs)))
 assert res<1e-6,res
 out=[]
 for j,load in enumerate(loads):
  volt={k:float(np.mean([v[idx[n],j] if n in idx else 0 for n in ns])) for k,ns in terms.items() if all(labels[n]==labels[src[0]] for n in ns)}
  out.append(dict(load_A=load,terminal_voltage_V=volt,kcl_residual_A=res,reference_pads=source,nodes_solved=len(unknown)))
 return out
ports={r:[a['ref']+'.'+a['number'] for a in pads if a['ref']==r] for r in ['J1','J2','J3','U6','U5']}
ports['U6']=['U6.10'] # Converter switching return is PGND, not an ideal short across every control GND pin.
ports['J1']=['J1.1','J1.12'] # USB ground contacts; shell is conductor, not an independently driven source.
rows=json.loads((E/('ground-extraction-'+label+'.json')).read_text())['rows'] if (E/('ground-extraction-'+label+'.json')).exists() else []
for area in [.03,.0075]:
 for factor in [1.,.8]:
  K,terms,stats=assemble(area,factor)
  results={}
  results['input_return']=solve(K,terms,ports['J1'],[{k:1/len(ports['U6']) for k in ports['U6']}])[0]
  results['output_returns']=solve(K,terms,ports['U6'],[{k:1/len(ports['J2']) for k in ports['J2']},{k:1/len(ports['J3']) for k in ports['J3']},{**{k:.127/len(ports['J2']) for k in ports['J2']},**{k:.127/len(ports['J3']) for k in ports['J3']}}])
  row=dict(max_triangle_area_mm2=area,track_width_factor=factor,mesh=stats,results_at_20C=results);rows.append(row);print('Mesh done',area,factor,stats,flush=True)
  save(E/('ground-extraction-'+label+'.json'),dict(utc=now(),board_sha256=digest(w/'main.kicad_pcb'),rows=rows,temperature_scaling='R(T)=R20*(1+0.00393*(T-20))',assumptions=dict(copper_um=35,barrel_um=20,z_mm=zmm,boundary_simplification_mm=.002,pad_and_via_landing_contact_ohm=1e-6,port_current='U6.10 PGND only; J1.1/12 USB return source, shell not driven; six equal current GH contacts. No ideal short among U6 control ground pins.'),limitations=['Linear triangular DC sheet FEM on actual GND fill polygons including holes and thermal spokes, actual GND tracks, pads and plated vias; source pad equipotential approximation','Width -20% applied to actual ground tracks; filled plane and thermal spokes use native geometry. Plane/thermal etch and actual stackup/plating/copper minima remain manufacturing inputs','Mesh convergence is a numerical check, not a manufacturing worst-case guarantee','No contact, harness or component resistance included; use separate system model']))
