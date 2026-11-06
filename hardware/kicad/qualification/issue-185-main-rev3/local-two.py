"""Bounded 0.025mm local grid routing, no ripup, placement or rule changes."""
from common import *
import pcbnew as p, numpy as np, shapely, heapq, math,shutil
sys.path.insert(0,str(E/'source183'))
from audit import pad_polygon,polygons,xy,point
from shapely.geometry import Point,LineString
from shapely.ops import unary_union
w=E/'local35';w.mkdir(exist_ok=True);b=p.LoadBoard(str(E/'straight33/main.kicad_pcb'));probes=json.loads((E/'source183/move-probes.json').read_text());records=[]
step=.025;guard=.00005
for r in probes:
 if r['straight_stub_candidate_mm'] is not None:continue
 tracks=list(b.GetTracks());vias=[t for t in tracks if isinstance(t,p.PCB_VIA)];v=next(t for t in vias if t.m_Uuid.AsString()==r['via_uuid']);net=v.GetNetname();layers=list(b.GetEnabledLayers().CuStack());org=r['origin_mm']
 pads=[(a,l,pad_polygon(a,l)) for f in b.GetFootprints() for a in f.Pads() if a.GetAttribute()!=p.PAD_ATTRIB_NPTH for l in layers if a.IsOnLayer(l)]
 foreign={l:unary_union([g for a,pl,g in pads if pl==l and a.GetNetname()!=net]+[Point(xy(t.GetPosition())).buffer(.3,quad_segs=128) if isinstance(t,p.PCB_VIA) else LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2,quad_segs=32) for t in tracks if t.GetNetname()!=net and t.IsOnLayer(l)]) for l in layers}
 # Existing local grid candidates from the #183 3mm envelope.
 coords=np.array([(round(org[0]+i*step,6),round(org[1]+j*step,6)) for i in range(-120,121) for j in range(-120,121)]);pts=shapely.points(coords);side=241
 body=shapely.distance(pts,unary_union([g for a,l,g in pads]))>=.4+guard
 for l in layers:body &= shapely.distance(pts,foreign[l])>=.4+guard
 body &= shapely.distance(pts,unary_union([Point(xy(t.GetPosition())).buffer(.3,quad_segs=128) for t in vias if t!=v]))>=.4+guard
 body &= np.linalg.norm(coords-np.array(org),axis=1)<=3
 outline=p.SHAPE_POLY_SET();assert b.GetBoardPolygonOutlines(outline);board=polygons(outline)
 body &= shapely.contains(board.buffer(-.6-guard),pts)
 for z in list(b.Zones())+[z for f in b.GetFootprints() for z in f.Zones()]:
  if z.GetIsRuleArea() and z.GetDoNotAllowVias():body &= shapely.distance(pts,polygons(z.Outline()))>=.3+guard
 for f in b.GetFootprints():
  for a in f.Pads():
   if a.GetAttribute()==p.PAD_ATTRIB_NPTH:body &= shapely.distance(pts,Point(xy(a.GetPosition())))>=p.ToMM(a.GetDrillSize().x)/2+.55+guard
 anchorpaths=[]
 for l in sorted({b.GetLayerID(a['layer']) for a in r['anchors']}):
  aa=[a for a in r['anchors'] if b.GetLayerID(a['layer'])==l];anchor=aa[0];start=anchor['position_mm'];width=max(a['width_mm'] for a in aa);assert width==.1
  obstacles=foreign[l].buffer(.15+guard,quad_segs=32)
  for z in list(b.Zones())+[z for f in b.GetFootprints() for z in f.Zones()]:
   if z.GetIsRuleArea() and z.GetDoNotAllowTracks() and z.IsOnLayer(l):obstacles=unary_union([obstacles,polygons(z.Outline()).buffer(.05+guard)])
  for f in b.GetFootprints():
   for a in f.Pads():
    if a.GetAttribute()==p.PAD_ATTRIB_NPTH:obstacles=unary_union([obstacles,Point(xy(a.GetPosition())).buffer(p.ToMM(a.GetDrillSize().x)/2+.30+guard)])
  allowed=~shapely.intersects(pts,obstacles)
  allowed &= shapely.contains(board.buffer(-.35-guard),pts)
  dist=np.full(len(coords),np.inf);prev=np.full(len(coords),-1,dtype=int);heap=[]
  near=np.flatnonzero(allowed & (np.linalg.norm(coords-np.array(start),axis=1)<.1))
  for idx in near:
   seg=LineString([start,coords[idx]])
   if not seg.intersects(obstacles):dist[idx]=seg.length;heapq.heappush(heap,(dist[idx],int(idx)))
  while heap:
   dd,idx=heapq.heappop(heap)
   if dd>dist[idx]+1e-9:continue
   ix,iy=divmod(idx,side)
   for di,dj in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
    nx,ny=ix+di,iy+dj
    if not (0<=nx<side and 0<=ny<side):continue
    ni=nx*side+ny
    if not allowed[ni]:continue
    nd=dd+step*math.hypot(di,dj)
    if nd>=dist[ni]-1e-9:continue
    if LineString([coords[idx],coords[ni]]).intersects(obstacles):continue
    dist[ni]=nd;prev[ni]=idx;heapq.heappush(heap,(nd,ni))
  body &= np.isfinite(dist);anchorpaths.append((l,start,width,dist,prev,obstacles))
  print(net,b.GetLayerName(l),'reachable',np.isfinite(dist).sum(),'joint candidates',body.sum(),flush=True)
 candidates=np.flatnonzero(body)
 if not len(candidates):
  save(w/('failure-'+net+'.json'),dict(via=r,reason='No joint candidate within 3mm with fixed copper and 0.025mm grid'));raise RuntimeError('local bound exhausted')
 target=min(candidates,key=lambda idx:sum(a[3][idx] for a in anchorpaths)+np.linalg.norm(coords[idx]-org)*.1);pos=coords[target].tolist();v.SetPosition(point(pos));paths=[]
 for l,start,width,dist,prev,obstacles in anchorpaths:
  cur=target;rev=[]
  while cur!=-1:rev.append(coords[cur].tolist());cur=prev[cur]
  path=[start]+rev[::-1];simple=[path[0]];i=0
  while i<len(path)-1:
   j=len(path)-1
   while j>i+1 and LineString([path[i],path[j]]).intersects(obstacles):j-=1
   simple.append(path[j]);i=j
  ids=[]
  for a,c in zip(simple,simple[1:]):
   if a==c:continue
   t=p.PCB_TRACK(b);t.SetStart(point(a));t.SetEnd(point(c));t.SetLayer(l);t.SetWidth(p.FromMM(width));t.SetNetCode(v.GetNetCode());b.Add(t);ids.append(t.m_Uuid.AsString())
  paths.append(dict(layer=b.GetLayerName(l),width_mm=width,points_mm=simple,track_uuids=ids))
 records.append(dict(via_uuid=r['via_uuid'],net=net,origin_mm=org,position_mm=pos,paths=paths,candidate_count=len(candidates),bounds=dict(radius_mm=3,grid_mm=step,no_ripup=True)))
 save(w/'changes.json',records)
print('Both local vias routed',flush=True)
shutil.copyfile(E/'straight33/main.kicad_pro',w/'main.kicad_pro');assert p.SaveBoard(str(w/'before-fill.kicad_pcb'),b);b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();assert p.SaveBoard(str(w/'main.kicad_pcb'),b)
