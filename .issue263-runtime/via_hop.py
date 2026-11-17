import pcbnew as p, sys, json, subprocess, shutil
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union
w=sys.argv[1]; padref=sys.argv[2]; padnum=sys.argv[3]; netname='GND'
src=w+'/main.kicad_pcb'
b=p.LoadBoard(src); b.BuildConnectivity()
# zone areas for GND on B.Cu
z=[z for z in b.Zones() if z.GetNetname()==netname][0]
fp=z.GetFilledPolysList(z.GetLayer()); areas=[]
for i in range(fp.OutlineCount()):
 ol=fp.Outline(i); pts=[(p.ToMM(ol.CPoint(j).x),p.ToMM(ol.CPoint(j).y)) for j in range(ol.PointCount())]
 if len(pts)>=3: areas.append(Polygon(pts))
f=[x for x in b.GetFootprints() if x.GetReference()==padref][0]
pad=[a for a in f.Pads() if a.GetNumber()==padnum][0]
pc=Point(p.ToMM(pad.GetPosition().x),p.ToMM(pad.GetPosition().y))
iso=[a for a in areas if a.buffer(0.02).contains(pc)]
main=[a for a in areas if a.area>100]
print('isolated area:', [round(a.area,2) for a in iso], 'mainland areas:', len(main))
iso=iso[0]; mainu=unary_union(main)
# foreign copper shapes per layer (pads+tracks of other nets), for screening
foreign={p.F_Cu:[],p.B_Cu:[]}
for f2 in b.GetFootprints():
 for a in f2.Pads():
  if a.GetNetname()==netname: continue
  for l in (p.F_Cu,p.B_Cu):
   if a.IsOnLayer(l):
    from shapely.geometry import box
    foreign[l].append(box(p.ToMM(a.GetPosition().x)-p.ToMM(a.GetSize().x)/2-0.10,p.ToMM(a.GetPosition().y)-p.ToMM(a.GetSize().y)/2-0.10,p.ToMM(a.GetPosition().x)+p.ToMM(a.GetSize().x)/2+0.10,p.ToMM(a.GetPosition().y)+p.ToMM(a.GetSize().y)/2+0.10))
for t in b.GetTracks():
 if t.GetNetname()==netname: continue
 if isinstance(t,p.PCB_VIA):
  for l in (p.F_Cu,p.B_Cu): foreign[l].append(Point(p.ToMM(t.GetPosition().x),p.ToMM(t.GetPosition().y)).buffer(p.ToMM(t.GetWidth(l))/2+0.10))
 else:
  foreign[t.GetLayer()].append(LineString([(p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y)),(p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y))]).buffer(p.ToMM(t.GetWidth())/2+0.10,cap_style=1))
fu={l:unary_union(v) for l,v in foreign.items()}
drills=[Point(p.ToMM(a.GetPosition().x),p.ToMM(a.GetPosition().y)).buffer((p.ToMM(a.GetDrillSize().x) or 300)/2000+0.25) for f2 in b.GetFootprints() for a in f2.Pads() if a.GetDrillSize().x>0]
drills+= [Point(p.ToMM(t.GetPosition().x),p.ToMM(t.GetPosition().y)).buffer(0.40) for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
du=unary_union(drills)
# candidate A points inside iso area (eroded by via radius+clearance to foreign B copper)
import itertools
cands=[]
minx,miny,maxx,maxy=iso.bounds
x=minx+0.35
while x<maxx-0.3:
 y=miny+0.35
 while y<maxy-0.3:
  pt=Point(x,y)
  if iso.buffer(-0.32).contains(pt) and not fu[p.B_Cu].intersects(pt.buffer(0.30)) and not du.intersects(pt.buffer(0.30)): cands.append(pt)
  y+=0.25
 x+=0.25
print('A candidates:', len(cands))
found=None
for A in cands:
 # B: points in mainland within 7mm, B.Cu-legal for a via
 for r in (2.0,3.0,4.0,5.0,6.0,7.0):
  for ang in range(0,360,15):
   import math
   B=Point(A.x+r*math.cos(math.radians(ang)), A.y+r*math.sin(math.radians(ang)))
   if not mainu.buffer(-0.32).contains(B): continue
   if fu[p.B_Cu].intersects(B.buffer(0.30)) or du.intersects(B.buffer(0.30)): continue
   seg=LineString([(A.x,A.y),(B.x,B.y)]).buffer(0.05+0.10,cap_style=1)
   if fu[p.F_Cu].intersects(seg): continue
   if fu[p.B_Cu].intersects(LineString([(A.x,A.y),(B.x,B.y)]).buffer(0.001)): pass
   found=(A,B); break
  if found: break
 if found: break
print('hop:', found)
if found:
 A,B=found
 net=b.FindNet(netname)
 def via(pt):
  v=p.PCB_VIA(b); v.SetPosition(p.VECTOR2I(int(pt.x*1e6),int(pt.y*1e6))); v.SetWidth(int(0.6e6)); v.SetDrill(int(0.3e6)); v.SetLayerPair(p.F_Cu,p.B_Cu); v.SetNet(net); b.Add(v)
 via(A); via(B)
 t=p.PCB_TRACK(b); t.SetStart(p.VECTOR2I(int(A.x*1e6),int(A.y*1e6))); t.SetEnd(p.VECTOR2I(int(B.x*1e6),int(B.y*1e6))); t.SetWidth(int(0.3e6)); t.SetLayer(p.F_Cu); t.SetNet(net); b.Add(t)
 p.SaveBoard(w+'/main-hop.kicad_pcb',b)
 print('saved main-hop.kicad_pcb')
