from common import *
import pcbnew as p,shutil,math
from shapely.geometry import LineString,Point,Polygon
w=E/'inspection/final';b=p.LoadBoard(str(w/'main.kicad_pcb'));regions=[];keep=[];removed=[]
for f in b.GetFootprints():
 if f.GetReference() not in ['J2','J3']:continue
 f.Reference().SetVisible(False)
 # Bounding polygon in the original connector frame, expanded for local fanout.
 angle=math.radians(f.GetOrientationDegrees());x,y=p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y)
 def xy(u,v):return [x+u*math.cos(angle)+v*math.sin(angle),y-u*math.sin(angle)+v*math.cos(angle)]
 regions.append(Polygon([xy(u,v) for u,v in [(-12,-5),(12,-5),(12,4),(-12,4)]]))
 for a in f.Pads():a.SetShape(p.PAD_SHAPE_RECT)
for t in list(b.GetTracks()):
 if isinstance(t,p.PCB_VIA):g=Point(p.ToMM(t.GetPosition().x),p.ToMM(t.GetPosition().y)).buffer(p.ToMM(t.GetWidth())/2)
 else:g=LineString([[p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y)],[p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y)]]).buffer(p.ToMM(t.GetWidth())/2)
 if any(g.intersects(r) for r in regions):
  removed.append(dict(uuid=t.m_Uuid.AsString(),net=t.GetNetname()));keep.append(t);b.Remove(t)
p.SaveBoard(str(T/'route-input.kicad_pcb'),b);shutil.copyfile(w/'main.kicad_pro',T/'route-input.kicad_pro')
save(E/'local-routing-scope.json',dict(regions_xy_mm=[list(r.exterior.coords) for r in regions],removed=removed,policy='Only copper intersecting these J2/J3 local regions is removed; surviving copper is fixed.'))
print(len(removed),'objects removed')
