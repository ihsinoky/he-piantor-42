"""Relocate only near-boundary vias with native-checked local stub updates."""
from pathlib import Path
import sys,math,json
import pcbnew as p
from shapely.geometry import Point,LineString
from verify import xy,polys
E=Path(__file__).resolve().parent;MM=1e6
V=lambda x,y:p.VECTOR2I(round(x*MM),round(y*MM))
def run(w):
 src=w/'main.kicad_pcb';b=p.LoadBoard(str(src));assert b
 manager=p.GetSettingsManager();manager.LoadProject(str(w/'main.kicad_pro'));b.SetProject(manager.Prj())
 pads=[a for f in b.GetFootprints() for a in f.Pads() if a.GetAttribute()!=p.PAD_ATTRIB_NPTH]
 holes=[a for f in b.GetFootprints() for a in f.Pads() if a.GetAttribute()==p.PAD_ATTRIB_NPTH]
 tracks=[t for t in b.GetTracks() if not isinstance(t,p.PCB_VIA)];vias=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
 outline=p.SHAPE_POLY_SET();b.GetBoardPolygonOutlines(outline);board=polys(outline)
 keepouts=[polys(z.Outline()) for z in b.Zones() if z.GetIsRuleArea()]
 def gap(v):return min(a.GetEffectiveShape(l).Distance(v.GetPosition())/MM-.3 for a in pads for l in (p.F_Cu,p.B_Cu) if a.IsOnLayer(l))
 changes=[]
 for v in vias:
  oldgap=gap(v)
  if oldgap>=.125-1e-9:continue
  old=v.GetPosition();origin=xy(old);anchors=[]
  for t in tracks:
   if t.GetStart()==old:anchors.append((t,True,t.GetEnd()))
   if t.GetEnd()==old:anchors.append((t,False,t.GetStart()))
  new_stubs=[]
  for l in (p.F_Cu,p.B_Cu):
   if any(a.IsOnLayer(l) and a.GetNetname()==v.GetNetname() and a.GetEffectiveShape(l).Collide(old) for a in pads):
    stub=p.PCB_TRACK(b);stub.SetStart(old);stub.SetEnd(old);stub.SetLayer(l);stub.SetWidth(p.FromMM(.3 if v.GetNetname() in ('HALL_5V','GND') else .1));stub.SetNetCode(v.GetNetCode());anchors.append((stub,True,old));new_stubs.append(stub)
  assert anchors,(w.name,v.m_Uuid.AsString(),'unanchored')
  found=False
  for rstep in range(1,81):
   r=.025*rstep
   for angle in range(0,360,10):
    pos=V(origin[0]+r*math.cos(math.radians(angle)),origin[1]+r*math.sin(math.radians(angle)));disk=p.SHAPE_CIRCLE(pos,300000)
    if any(a.GetEffectiveShape(l).Distance(pos)/MM-.3<.125 for a in pads for l in (p.F_Cu,p.B_Cu) if a.IsOnLayer(l)):continue
    if not board.buffer(-.601).contains(Point(xy(pos))):continue
    if any(Point(xy(pos)).distance(k)<.301 for k in keepouts):continue
    if any(math.dist(xy(pos),xy(a.GetPosition()))<p.ToMM(a.GetDrillSize().x)/2+.551 for a in holes):continue
    if any(math.dist(xy(pos),xy(o.GetPosition()))<(.701 if o.GetNetname()!=v.GetNetname() else .551) for o in list(b.GetTracks()) if isinstance(o,p.PCB_VIA) and o.m_Uuid.AsString()!=v.m_Uuid.AsString()):continue
    if any(t.GetNetname()!=v.GetNetname() and t.GetEffectiveShape(t.GetLayer()).Collide(disk,100001) for t in tracks):continue
    valid=True
    for t,start,other in anchors:
     shape=p.SHAPE_SEGMENT(pos,other,t.GetWidth());l=t.GetLayer();g=LineString([xy(pos),xy(other)]).buffer(t.GetWidth()/2/MM)
     if any(a.GetNetname()!=v.GetNetname() and a.IsOnLayer(l) and a.GetEffectiveShape(l).Collide(shape,100001) for a in pads):valid=False;break
     if any(o.GetNetname()!=v.GetNetname() and o.GetLayer()==l and o.GetEffectiveShape(l).Collide(shape,100001) for o in tracks):valid=False;break
     if any(o.GetNetname()!=v.GetNetname() and g.distance(Point(xy(o.GetPosition())))<.400001 for o in b.GetTracks() if isinstance(o,p.PCB_VIA)):valid=False;break
     if any(g.intersects(k) for k in keepouts) or any(g.distance(Point(xy(a.GetPosition())))<p.ToMM(a.GetDrillSize().x)/2+.251 for a in holes):valid=False;break
    if not valid:continue
    v.SetPosition(pos)
    for t,start,other in anchors:
     if start:t.SetStart(pos)
     else:t.SetEnd(pos)
    for stub in new_stubs:b.Add(stub);tracks.append(stub)
    changes.append(dict(via_uuid=v.m_Uuid.AsString(),origin_mm=origin,new_mm=xy(pos),gap_before_mm=oldgap,gap_after_mm=gap(v)));found=True;break
   if found:break
  if not found:
   assert v.GetNetname() in ('HALL_5V','GND'),(w.name,'no via margin relocation',v.m_Uuid.AsString(),origin,oldgap)
   changes.append(dict(via_uuid=v.m_Uuid.AsString(),origin_mm=origin,gap_before_mm=oldgap,action='remove redundant power via; full connectivity requalification required'));b.Delete(v)
 b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity()
 assert p.SaveBoard(str(w/'main.kicad_pcb'),b)
 (w/'via-margin.json').write_text(json.dumps(changes,indent=2)+'\n');print(w.name,'moved',len(changes),flush=True)
if __name__=='__main__':
 for name in sys.argv[1:]:run(E/name)
