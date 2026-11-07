"""Search a conservative local via relocation; retain every original track and add stubs."""
from common import *
import pcbnew as p,numpy as np,shapely,math,collections,shutil
from shapely.geometry import Point,LineString
from shapely.ops import unary_union
import importlib.util
spec=importlib.util.spec_from_file_location('audit',E/'audit-vias.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
w=E/'runs/local01';w.mkdir(parents=True,exist_ok=True)
b=p.LoadBoard(str(E/'inspection/auto02/main.kicad_pcb'));layers=list(b.GetEnabledLayers().CuStack());tracks=list(b.GetTracks());v=next(t for t in tracks if t.m_Uuid.AsString()=='8666f08c-32a9-484e-a921-694042623510');org=a.xy(v.GetPosition());net=v.GetNetname()
pads=[(pad,l,a.pad_polygon(pad,l)) for f in b.GetFootprints() for pad in f.Pads() if pad.GetAttribute()!=p.PAD_ATTRIB_NPTH for l in layers if pad.IsOnLayer(l)]
foreign={l:unary_union([g for pad,pl,g in pads if pl==l and pad.GetNetname()!=net]+[Point(a.xy(t.GetPosition())).buffer(.3,quad_segs=128) if isinstance(t,p.PCB_VIA) else LineString([a.xy(t.GetStart()),a.xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2,quad_segs=32) for t in tracks if t.GetNetname()!=net and t.IsOnLayer(l)]) for l in layers}
allpads=unary_union([g for _,_,g in pads]);others=unary_union([Point(a.xy(t.GetPosition())).buffer(.3,quad_segs=128) for t in tracks if isinstance(t,p.PCB_VIA) and t!=v])
anchors=set()
for t in tracks:
 if isinstance(t,p.PCB_VIA) or t.GetNetname()!=net:continue
 if LineString([a.xy(t.GetStart()),a.xy(t.GetEnd())]).distance(Point(org))<.000002:anchors.add(t.GetLayer())
for pad,l,g in pads:
 if pad.GetNetname()==net and g.covers(Point(org)):anchors.add(l)
print('anchors',anchors,flush=True)
coords=np.array([(round(org[0]+i*.025,6),round(org[1]+j*.025,6)) for i in range(-100,101) for j in range(-100,101)])
pts=shapely.points(coords);ok=shapely.distance(pts,allpads)>=.42505
ok &= shapely.distance(pts,others)>=.40005
for l in layers:ok &= shapely.distance(pts,foreign[l])>=.40005
import heapq
side=201;paths=[]
for l in sorted(anchors):
 obstacles=foreign[l].buffer(.15005,quad_segs=32)
 allowed=~shapely.intersects(pts,obstacles)
 dist=np.full(len(coords),np.inf);prev=np.full(len(coords),-1,dtype=int);heap=[]
 center=100*side+100;assert allowed[center]
 dist[center]=0.;heapq.heappush(heap,(0.,center))
 while heap:
  dd,i=heapq.heappop(heap)
  if dd>dist[i]+1e-9:continue
  ix,iy=divmod(i,side)
  for di,dj in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
   nx,ny=ix+di,iy+dj
   if not (0<=nx<side and 0<=ny<side):continue
   j=nx*side+ny
   if not allowed[j]:continue
   nd=dd+.025*math.hypot(di,dj)
   if nd>=dist[j]-1e-9:continue
   if LineString([coords[i],coords[j]]).intersects(obstacles):continue
   dist[j]=nd;prev[j]=i;heapq.heappush(heap,(nd,j))
 ok &= np.isfinite(dist);paths.append((l,dist,prev,obstacles));print('layer reachable',l,np.isfinite(dist).sum(),'joint',ok.sum(),flush=True)
candidates=np.flatnonzero(ok);assert len(candidates),'No local candidate'
target=min(candidates,key=lambda i:sum(q[1][i] for q in paths));chosen=coords[target].tolist()
v.SetPosition(a.point(chosen));ids=[];pathrows=[]
for l,dist,prev,obstacles in paths:
 cur=target;rev=[]
 while cur!=-1:rev.append(coords[cur].tolist());cur=prev[cur]
 path=rev[::-1];simple=[path[0]];i=0
 while i<len(path)-1:
  j=len(path)-1
  while j>i+1 and LineString([path[i],path[j]]).intersects(obstacles):j-=1
  simple.append(path[j]);i=j
 rowids=[]
 for aa,bb in zip(simple,simple[1:]):
  t=p.PCB_TRACK(b);t.SetStart(a.point(aa));t.SetEnd(a.point(bb));t.SetWidth(p.FromMM(.1));t.SetLayer(l);t.SetNetCode(v.GetNetCode());b.Add(t);ids.append(t.m_Uuid.AsString());rowids.append(t.m_Uuid.AsString())
 pathrows.append(dict(layer=b.GetLayerName(l),points_mm=simple,uuids=rowids))
p.SaveBoard(str(w/'out.kicad_pcb'),b)
save(w/'changes.json',dict(via_uuid=v.m_Uuid.AsString(),net=net,origin_mm=org,position_mm=chosen,stubs=ids,layers=[b.GetLayerName(l) for l in sorted(anchors)],all_pad_target_mm=.125,minimum_candidate_gap_mm=Point(chosen).distance(allpads)-.3,paths=pathrows,method='Exhaustive 0.025mm grid +/-2.5mm; collision-free Dijkstra paths; no removed copper'))
print('moved',org,chosen,flush=True)
