"""Native-checked 0.30mm dogbones from top GND pads to the rear ground pour.
Adds separate, short ground returns where the general autorouter was boxed in.
"""
from pathlib import Path
import json,math,sys,shapely
import pcbnew as p
from shapely.geometry import Point,LineString
from verify import polys,xy
E=Path(__file__).resolve().parent;MM=1e6
V=lambda pos:p.VECTOR2I(round(pos[0]*MM),round(pos[1]*MM))
for name in sys.argv[1:]:
 w=E/name;b=p.LoadBoard(str(w/'power-repaired.kicad_pcb'));assert b
 manager=p.GetSettingsManager();manager.LoadProject(str(w/'input.kicad_pro'));b.SetProject(manager.Prj());b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity()
 pads=[(f,a) for f in b.GetFootprints() for a in f.Pads() if a.GetAttribute()!=p.PAD_ATTRIB_NPTH];holes=[a for f in b.GetFootprints() for a in f.Pads() if a.GetAttribute()==p.PAD_ATTRIB_NPTH]
 zones=[polys(z.GetFilledPolysList(p.B_Cu)) for z in b.Zones() if not z.GetIsRuleArea() and z.IsOnLayer(p.B_Cu) and z.GetNetname()=='GND'];ground=__import__('shapely').ops.unary_union(zones)
 outline=p.SHAPE_POLY_SET();b.GetBoardPolygonOutlines(outline);board=polys(outline);keepouts=[polys(z.Outline()) for z in b.Zones() if z.GetIsRuleArea()]
 groundcore=ground.buffer(-.301);boardcore=board.buffer(-.601);shapely.prepare(groundcore);shapely.prepare(boardcore);result=[]
 for f,a in pads:
  if a.GetNetname()!='GND' or not a.IsOnLayer(p.F_Cu):continue
  origin=xy(a.GetPosition());found=False
  # Existing valid, direct top dogbones are not duplicated.
  for t in b.GetTracks():
   if not isinstance(t,p.PCB_VIA) and t.GetNetname()=='GND' and t.GetLayer()==p.F_Cu and (t.GetStart()==a.GetPosition() or t.GetEnd()==a.GetPosition()):found=True;break
  if found:continue
  alltracks=b.GetTracks();vias=[t for t in alltracks if isinstance(t,p.PCB_VIA)];tracks=[t for t in alltracks if not isinstance(t,p.PCB_VIA)]
  for rr in range(12,81):
   radius=.05*rr
   for angle in range(0,360,5):
    new=[origin[0]+radius*math.cos(math.radians(angle)),origin[1]+radius*math.sin(math.radians(angle))];pos=V(new);pt=Point(xy(pos))
    if not groundcore.contains(pt) or not boardcore.contains(pt):continue
    if any(aa.GetEffectiveShape(l).Distance(pos)/MM-.3<.125 for ff,aa in pads for l in (p.F_Cu,p.B_Cu) if aa.IsOnLayer(l)):continue
    if any(pt.distance(k)<.301 for k in keepouts):continue
    if any(pt.distance(Point(xy(h.GetPosition())))<p.ToMM(h.GetDrillSize().x)/2+.551 for h in holes):continue
    if any(math.dist(new,xy(o.GetPosition()))<(.701 if o.GetNetname()!='GND' else .551) for o in vias):continue
    disk=p.SHAPE_CIRCLE(pos,300000)
    if any(t.GetNetname()!='GND' and t.GetEffectiveShape(t.GetLayer()).Collide(disk,100001) for t in tracks):continue
    stub=p.PCB_TRACK(b);stub.SetStart(a.GetPosition());stub.SetEnd(pos);stub.SetWidth(300000);stub.SetLayer(p.F_Cu);stub.SetNetCode(a.GetNetCode());shape=stub.GetEffectiveShape(p.F_Cu);g=LineString([origin,new]).buffer(.15)
    if any(aa.GetNetname()!='GND' and aa.IsOnLayer(p.F_Cu) and aa.GetEffectiveShape(p.F_Cu).Collide(shape,100001) for ff,aa in pads):continue
    if any(t.GetNetname()!='GND' and t.IsOnLayer(p.F_Cu) and t.GetEffectiveShape(p.F_Cu).Collide(shape,100001) for t in alltracks):continue
    if any(g.intersects(k) for k in keepouts) or any(g.distance(Point(xy(h.GetPosition())))<p.ToMM(h.GetDrillSize().x)/2+.251 for h in holes):continue
    via=p.PCB_VIA(b);via.SetPosition(pos);via.SetWidth(600000);via.SetDrill(300000);via.SetViaType(p.VIATYPE_THROUGH);via.SetLayerPair(p.F_Cu,p.B_Cu);via.SetNetCode(a.GetNetCode());b.Add(stub);b.Add(via)
    result.append(dict(pad=f.GetReference()+'.'+a.GetNumber(),origin_mm=origin,via_mm=xy(pos)));found=True;break
   if found:break
  if not found:result.append(dict(pad=f.GetReference()+'.'+a.GetNumber(),status='no direct dogbone; needs reroute'))
 # Remove copied pours before the controlled final refill.
 for z in list(b.Zones()):
  if not z.GetIsRuleArea():b.Delete(z)
 p.SaveBoard(str(w/'tapped.kicad_pcb'),b);(w/'ground-taps.json').write_text(json.dumps(result,indent=2)+'\n');print(w.name,result,flush=True)
