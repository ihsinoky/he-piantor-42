"""Batch native-checked power dogbones, then one refill; acceptance is separate.
Opposite-layer filled copper must fully contain each proposed via disk. All
pads (same-net included) constrain vias. No footprint or pad is changed.
"""
from pathlib import Path
import sys,json,math
import pcbnew as p
from shapely.geometry import Point,LineString
from shapely.ops import unary_union
from verify import xy,polys,padgeom
E=Path(__file__).resolve().parent;V=lambda a:p.VECTOR2I(round(a[0]*1e6),round(a[1]*1e6))
for name in sys.argv[1:]:
 w=E/name;b=p.LoadBoard(str(w/'main.kicad_pcb'));mgr=p.GetSettingsManager();mgr.LoadProject(str(w/'main.kicad_pro'));b.SetProject(mgr.Prj())
 pads=[(f,a,{l:a.GetEffectiveShape(l) for l in (p.F_Cu,p.B_Cu) if a.IsOnLayer(l)}) for f in b.GetFootprints() for a in f.Pads() if a.GetAttribute()!=p.PAD_ATTRIB_NPTH]
 holes=[a for f in b.GetFootprints() for a in f.Pads() if a.GetAttribute()==p.PAD_ATTRIB_NPTH]
 fixed=unary_union([polys(z.Outline()) for z in b.Zones() if z.GetIsRuleArea()]+[Point(xy(a.GetPosition())).buffer(p.ToMM(a.GetDrillSize().x)/2+.25) for a in holes])
 outline=p.SHAPE_POLY_SET();b.GetBoardPolygonOutlines(outline);core=polys(outline).buffer(-.61)
 history=[]
 for net,layer in [('HALL_5V',p.F_Cu),('GND',p.B_Cu)]:
  plane=unary_union([polys(z.GetFilledPolysList(layer)) for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname()==net and z.IsOnLayer(layer)])
  for f,a,shapes in pads:
   if a.GetNetname()!=net:continue
   own=p.F_Cu if a.IsOnLayer(p.F_Cu) else p.B_Cu
   if own==layer:continue
   origin=xy(a.GetPosition());position=a.GetPosition();found=False
   for item in b.GetTracks():
    if item.GetNetname()!=net or isinstance(item,p.PCB_VIA) or item.GetLayer()!=own:continue
    if item.GetEffectiveShape(own).Collide(a.GetEffectiveShape(own)):found=True;break
   if found:continue
   tracks=list(b.GetTracks())
   for radius in (.65,.8,1.,1.2,1.5,1.8,2.,2.4,3.,3.5,4.):
    for angle in range(0,360,10):
     pos=V([origin[0]+radius*math.cos(math.radians(angle)),origin[1]+radius*math.sin(math.radians(angle))]);point=Point(xy(pos));disk=point.buffer(.3,quad_segs=64)
     if not core.contains(point) or disk.distance(fixed)<.001 or disk.difference(plane).area>1e-9:continue
     if any(shape.Distance(pos)/1e6-.3<.135 for _,aa,ss in pads for shape in ss.values()):continue
     track=p.PCB_TRACK(b);track.SetStart(position);track.SetEnd(pos);track.SetLayer(own);track.SetWidth(300000);track.SetNetCode(a.GetNetCode());stub=track.GetEffectiveShape(own);g=LineString([origin,xy(pos)]).buffer(.15)
     if g.intersects(fixed):continue
     if any(aa.GetNetname()!=net and own in ss and ss[own].Collide(stub,110000) for _,aa,ss in pads):continue
     valid=True
     for t in tracks:
      if t.GetNetname()==net:continue
      if isinstance(t,p.PCB_VIA):
       if point.distance(Point(xy(t.GetPosition())))<.71 or (t.IsOnLayer(own) and t.GetEffectiveShape(own).Collide(stub,110000)):valid=False;break
      elif t.GetEffectiveShape(t.GetLayer()).Collide(p.SHAPE_CIRCLE(pos,300000),110000) or (t.GetLayer()==own and t.GetEffectiveShape(own).Collide(stub,110000)):valid=False;break
     if not valid:continue
     via=p.PCB_VIA(b);via.SetPosition(pos);via.SetWidth(600000);via.SetDrill(300000);via.SetViaType(p.VIATYPE_THROUGH);via.SetLayerPair(p.F_Cu,p.B_Cu);via.SetNetCode(a.GetNetCode());b.Add(track);b.Add(via);found=True
     history.append(dict(pad=f.GetReference()+'.'+a.GetNumber(),net=net,via_mm=xy(pos)));break
    if found:break
   if not found:history.append(dict(pad=f.GetReference()+'.'+a.GetNumber(),net=net,status='requires general repair'))
 b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();p.SaveBoard(str(w/'main.kicad_pcb'),b)
 (w/'power-taps.json').write_text(json.dumps(history,indent=2)+'\n');print(name,len(history),'batch taps',sum('via_mm' in r for r in history),flush=True)
