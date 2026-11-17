import pcbnew as p, sys
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
w=sys.argv[1]; net=sys.argv[2] if len(sys.argv)>2 else 'GND'
b=p.LoadBoard(w+'/main.kicad_pcb'); b.BuildConnectivity()
# copper pieces: pads (as boxes), tracks (as buffered lines), vias (circles), zone fills
pieces=[]  # (geom, layerset, label)
def buf_line(a,b_,wd): 
 from shapely.geometry import LineString
 return LineString([(p.ToMM(a.x),p.ToMM(a.y)),(p.ToMM(b_.x),p.ToMM(b_.y))]).buffer(wd/2,cap_style=1)
for f in b.GetFootprints():
 for a in f.Pads():
  if a.GetNetname()!=net: continue
  layers={l for l in (p.F_Cu,p.B_Cu) if a.IsOnLayer(l)}
  g=box(p.ToMM(a.GetPosition().x)-p.ToMM(a.GetSize().x)/2,p.ToMM(a.GetPosition().y)-p.ToMM(a.GetSize().y)/2,p.ToMM(a.GetPosition().x)+p.ToMM(a.GetSize().x)/2,p.ToMM(a.GetPosition().y)+p.ToMM(a.GetSize().y)/2)
  pieces.append((g,layers,f'{f.GetReference()}.{a.GetNumber()}'))
for t in b.GetTracks():
 if t.GetNetname()!=net: continue
 if isinstance(t,p.PCB_VIA):
  g=Point(p.ToMM(t.GetPosition().x),p.ToMM(t.GetPosition().y)).buffer(p.ToMM(t.GetWidth())/2)
  pieces.append((g,{p.F_Cu,p.B_Cu},'via'))
 else:
  pieces.append((buf_line(t.GetStart(),t.GetEnd(),p.ToMM(t.GetWidth())),{t.GetLayer()},'track'))
for z in b.Zones():
 if z.GetNetname()!=net: continue
 fp=z.GetFilledPolysList(z.GetLayer())
 for i in range(fp.OutlineCount()):
  ol=fp.Outline(i); pts=[(p.ToMM(ol.CPoint(j).x),p.ToMM(ol.CPoint(j).y)) for j in range(ol.PointCount())]
  if len(pts)>=3: pieces.append((Polygon(pts),{z.GetLayer()},'zone'))
# union-find per layer-aware overlap: two pieces connect if they share a layer and overlap
n=len(pieces); parent=list(range(n))
def find(x):
 while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
 return x
for i in range(n):
 for j in range(i+1,n):
  if pieces[i][1]&pieces[j][1] and pieces[i][0].intersects(pieces[j][0]): parent[find(i)]=find(j)
from collections import defaultdict
comps=defaultdict(list)
for i in range(n): comps[find(i)].append(pieces[i][2])
print('components:', len(comps))
for c in sorted(comps.values(), key=len):
 pads=[x for x in c if not x.startswith(('track','via','zone'))]
 print(' size', len(c), 'pads:', pads[:14])
