"""Automatic local copper repair, frozen placement, no relaxed fabrication rules.
Grid A* joins physical copper components. All proposed segments/vias receive
native-shape clearance checks before insertion. Full independent DRC follows.
"""
from pathlib import Path
import sys,json,math,subprocess,collections
import numpy as np
import shapely
from shapely.geometry import Point,LineString,Polygon,box
from shapely.ops import unary_union
import pcbnew as p
from verify import polys,padgeom,xy
E=Path(__file__).resolve().parent;T=E.parents[4];V=lambda xy:p.VECTOR2I(round(xy[0]*1e6),round(xy[1]*1e6))

def run(w):
 src=w/'continued.kicad_pcb' if (w/'continued.kicad_pcb').exists() else w/'routed.kicad_pcb'
 b=p.LoadBoard(str(src));assert b
 manager=p.GetSettingsManager();manager.LoadProject(str(w/'input.kicad_pro'));b.SetProject(manager.Prj())
 # Widen forbidden neckdowns before repairs. A subsequent DRC must prove them.
 narrow=[]
 for t in b.GetTracks():
  if not isinstance(t,p.PCB_VIA) and t.GetNetname() in ('GND','HALL_5V') and t.GetWidth()<300000:
   narrow.append(t.m_Uuid.AsString());b.Delete(t) # Never widen through existing foreign copper.
 # Rebuild only the service routing window; preserve all copper outside it.
 cuts=[]
 service=box(60 if w.name.endswith('left') else 93,118.0,108 if w.name.endswith('left') else 146,133.2)
 for t in list(b.GetTracks()):
  geom=Point(xy(t.GetPosition())) if isinstance(t,p.PCB_VIA) else LineString([xy(t.GetStart()),xy(t.GetEnd())])
  if not geom.intersects(service):continue
  cuts.append(dict(net=t.GetNetname(),uuid=t.m_Uuid.AsString(),kind=t.GetClass()))
  if not isinstance(t,p.PCB_VIA):
   outside=geom.difference(service.buffer(.01))
   for line in outside.geoms if hasattr(outside,'geoms') else [outside]:
    if line.is_empty or line.length<.001:continue
    other=p.PCB_TRACK(b);other.SetStart(V(line.coords[0]));other.SetEnd(V(line.coords[-1]));other.SetWidth(t.GetWidth());other.SetLayer(t.GetLayer());other.SetNetCode(t.GetNetCode());b.Add(other)
  b.Delete(t)
 pads=[(f,a) for f in b.GetFootprints() for a in f.Pads() if a.GetAttribute()!=p.PAD_ATTRIB_NPTH]
 holes=[a for f in b.GetFootprints() for a in f.Pads() if a.GetAttribute()==p.PAD_ATTRIB_NPTH]
 outline=p.SHAPE_POLY_SET();assert b.GetBoardPolygonOutlines(outline);board=polys(outline)
 # Region includes every service component and TP, and lower thumb for spill paths.
 x0,y0,x1,y1=board.bounds;y0=max(y0,108.0);step=.05
 nx=round((x1-x0)/step)+1;ny=round((y1-y0)/step)+1
 xx,yy=np.meshgrid(x0+np.arange(nx)*step,y0+np.arange(ny)*step);points=shapely.points(xx.ravel(),yy.ravel());n=len(points)
 fixed=unary_union([Point(xy(a.GetPosition())).buffer(p.ToMM(a.GetDrillSize().x)/2+.25) for a in holes]+[polys(z.Outline()) for z in b.Zones() if z.GetIsRuleArea()])
 records=[]
 def elements(net):
  result=[]
  for f,a in pads:
   if a.GetNetname()!=net:continue
   for l in (p.F_Cu,p.B_Cu):
    if a.IsOnLayer(l):result.append((padgeom(a,l),l,True))
  for t in b.GetTracks():
   if t.GetNetname()!=net:continue
   if isinstance(t,p.PCB_VIA):
    geom=Point(xy(t.GetPosition())).buffer(.3).difference(Point(xy(t.GetPosition())).buffer(.15))
    result.extend((geom,l,False) for l in (p.F_Cu,p.B_Cu))
   else:result.append((LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2),t.GetLayer(),False))
  return result
 def groups(net):
  # Actual copper union on each layer, joined by physical via annuli.
  es=elements(net);parent=list(range(len(es)))
  def find(i):
   while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
   return i
  tree=shapely.STRtree([a[0] for a in es])
  for i,(g,l,_) in enumerate(es):
   for jj in tree.query(g,predicate='intersects'):
    j=int(jj)
    if j>=i:continue
    if l==es[j][1]:parent[find(i)]=find(j)
  # Vias bridge F and B annuli; duplicate shapes in es can be matched exactly.
  for i in range(len(es)-1):
   if not es[i][2] and es[i][1]!=es[i+1][1] and es[i][0].equals(es[i+1][0]):parent[find(i)]=find(i+1)
  out=collections.defaultdict(list)
  for i,a in enumerate(es):out[find(i)].append(a)
  return [g for g in out.values() if any(a[2] for a in g)]
 nets=['WING_EN','MUX_A2','MUX_A1','MUX_A0']+['H_'+group+str(i)+'_RAW' for group in 'ABC' for i in range(7)]+['MUX_OUT_'+g for g in 'ABC']+['GND','HALL_5V']
 for net in nets:
  if net in ('GND','HALL_5V'):continue # Reconnected after pour.
  for attempt in range(10):
   gs=groups(net)
   if len(gs)<=1:break
   gs.sort(key=lambda g:-sum(a[0].area for a in g));source=gs[0];target=gs[1]
   print(w.name,net,'groups',len(gs),'target bounds',unary_union([a[0] for a in target]).bounds,flush=True)
   width=.1;blocked=[];foreign={l:[] for l in (p.F_Cu,p.B_Cu)};native={l:[] for l in foreign}
   for f,a in pads:
    if a.GetNetname()==net:continue
    for l in foreign:
     if a.IsOnLayer(l):foreign[l].append(padgeom(a,l));native[l].append(a.GetEffectiveShape(l))
   for t in b.GetTracks():
    if t.GetNetname()==net:continue
    if isinstance(t,p.PCB_VIA):geom=Point(xy(t.GetPosition())).buffer(.3);ls=list(foreign)
    else:geom=LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2);ls=[t.GetLayer()]
    for l in ls:foreign[l].append(geom);native[l].append(t.GetEffectiveShape(l))
   for l in foreign:
    obs=unary_union(foreign[l]).buffer(width/2+.105).union(fixed.buffer(width/2+.005))
    shapely.prepare(obs);inside=board.buffer(-.3-width/2-.005);shapely.prepare(inside)
    blocked.append(shapely.intersects(obs,points)|~shapely.contains(inside,points))
   allpads=unary_union([padgeom(a,l) for f,a in pads for l in foreign if a.IsOnLayer(l)])
   viaobs=unary_union([unary_union(foreign[l]).buffer(.405) for l in foreign]+[allpads.buffer(.455),fixed.buffer(.305)])
   shapely.prepare(viaobs);inside=board.buffer(-.605);shapely.prepare(inside)
   via=shapely.intersects(viaobs,points)|~shapely.contains(inside,points)
   masks=[]
   for group in (source,target):
    layer_masks=[]
    for l in foreign:
     g=unary_union([a[0] for a in group if a[1]==l]);shapely.prepare(g);layer_masks.append(shapely.intersects(g,points))
    masks.append(np.concatenate(layer_masks).astype(np.uint8))
   data=np.array([nx,ny],dtype=np.int32).tobytes()+np.concatenate(blocked).astype(np.uint8).tobytes()+via.astype(np.uint8).tobytes()+masks[0].tobytes()+masks[1].tobytes()
   pathin=T/(w.name+'-grid.bin');pathout=T/(w.name+'-path.bin');pathin.write_bytes(data)
   rc=subprocess.run([str(T/'grid-search'),str(pathin),str(pathout)]).returncode
   if rc:print(w.name,net,'NO LOCAL PATH',flush=True);break
   path=np.frombuffer(pathout.read_bytes(),dtype=np.int32);ls=list(foreign)
   def pos(q):return [float(xx.ravel()[q%n]),float(yy.ravel()[q%n])]
   # Collapse collinear grid steps, preserving every layer transition.
   nodes=[int(path[0])]
   for i in range(1,len(path)-1):
    if path[i]-path[i-1]!=path[i+1]-path[i]:nodes.append(int(path[i]))
   nodes.append(int(path[-1]));new=[]
   for a,z in zip(nodes,nodes[1:]):
    if a//n!=z//n:
     v=p.PCB_VIA(b);v.SetPosition(V(pos(a)));v.SetWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNetCode(b.FindNet(net).GetNetCode());new.append(v)
    else:
     t=p.PCB_TRACK(b);t.SetStart(V(pos(a)));t.SetEnd(V(pos(z)));t.SetWidth(p.FromMM(width));t.SetLayer(ls[a//n]);t.SetNetCode(b.FindNet(net).GetNetCode());new.append(t)
   for t in new:
    if isinstance(t,p.PCB_VIA):
     for f,a in pads:
      for l in foreign:
       if a.IsOnLayer(l):assert a.GetEffectiveShape(l).Distance(t.GetPosition())/1e6-.3>=.15-1e-6
    else:
     shape=t.GetEffectiveShape(t.GetLayer());assert not any(a.Collide(shape,p.FromMM(.1)) for a in native[t.GetLayer()]),(net,'native collision')
   for t in new:b.Add(t)
   records.append(dict(net=net,segments=sum(not isinstance(t,p.PCB_VIA) for t in new),vias=sum(isinstance(t,p.PCB_VIA) for t in new),nodes=[dict(position_mm=pos(q),layer=b.GetLayerName(ls[q//n])) for q in nodes]))
   print(w.name,net,len(gs),'->',len(groups(net)),flush=True)
 b.BuildConnectivity();p.SaveBoard(str(w/'repaired.kicad_pcb'),b)
 (w/'local-repair.json').write_text(json.dumps(dict(source=src.name,removed_neckdowns=narrow,local_blocker_cuts=cuts,paths=records),indent=2)+'\n')
if __name__=='__main__':
 for name in sys.argv[1:]:run(E/name)
