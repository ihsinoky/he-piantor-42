"""Final bounded service-power escape repair, using physical major-plane landing.
Never rips foreign copper or lands in the pad's own island. Post-audit mandatory.
"""
from pathlib import Path
import sys,json,math,importlib.util
import pcbnew as p
from shapely.geometry import Point
from shapely.ops import unary_union
from verify import xy,polys
E=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('plane',E/'plane-repair.py');r=importlib.util.module_from_spec(sp);sp.loader.exec_module(r)
name=sys.argv[1];w=E/name;b=p.LoadBoard(str(w/'main.kicad_pcb'));mgr=p.GetSettingsManager();mgr.LoadProject(str(w/'input.kicad_pro'));b.SetProject(mgr.Prj());V=lambda q:p.VECTOR2I(round(q[0]*1e6),round(q[1]*1e6))
outline=p.SHAPE_POLY_SET();b.GetBoardPolygonOutlines(outline);board=polys(outline);pads=[(f,a) for f in b.GetFootprints() for a in f.Pads()];records=[]
for net in ('HALL_5V','GND'):
 groups=r.components(b,net)
 if len(groups)<2:continue
 major=max(groups,key=lambda g:sum(a[2] for a in g));landing=unary_union([a[0] for a in major if p.F_Cu in a[1]]).buffer(-.02)
 for group in groups:
  if group is major:continue
  for f,pad in pads:
   if not f.GetReference().startswith('U_MUX_') or pad.GetNetname()!=net:continue
   pg=r.padgeom(pad,p.B_Cu)
   if not any(a[2] and a[0].intersects(pg) for a in group):continue
   px,py=xy(pad.GetPosition());cx,cy=xy(f.GetPosition());theta=math.atan2(py-cy,px-cx);attempts=0;chosen=None;tracks=list(b.GetTracks())
   for delta in [0]+[v for i in range(5,91,5) for v in (i,-i)]:
    if chosen:break
    for rr in range(12,81):
     attempts+=1;dist=rr/10;ang=theta+math.radians(delta);target=[px+dist*math.cos(ang),py+dist*math.sin(ang)];q=V(target)
     if not board.buffer(-.601).contains(Point(target)) or not landing.contains(Point(target)):continue
     if any(isinstance(t,p.PCB_VIA) and math.dist(xy(t.GetPosition()),target)<.550001 for t in tracks):continue
     if any(a.GetEffectiveShape(l).Distance(q)/1e6-.3<.125 for _,a in pads for l in (p.F_Cu,p.B_Cu) if a.IsOnLayer(l)):continue
     stub=p.PCB_TRACK(b);stub.SetStart(pad.GetPosition());stub.SetEnd(q);stub.SetLayer(p.B_Cu);stub.SetWidth(300000);stub.SetNetCode(pad.GetNetCode());shape=stub.GetEffectiveShape(p.B_Cu);disk=p.SHAPE_CIRCLE(q,300000)
     if any(a.GetNetname()!=net and a.IsOnLayer(p.B_Cu) and a.GetEffectiveShape(p.B_Cu).Collide(shape,100001) for _,a in pads):continue
     if any(t.GetNetname()!=net and (t.GetEffectiveShape(t.GetLayer()).Collide(disk,100001) or (t.IsOnLayer(p.B_Cu) and t.GetEffectiveShape(p.B_Cu).Collide(shape,100001))) for t in tracks):continue
     via=p.PCB_VIA(b);via.SetPosition(q);via.SetWidth(600000);via.SetDrill(300000);via.SetViaType(p.VIATYPE_THROUGH);via.SetLayerPair(p.F_Cu,p.B_Cu);via.SetNetCode(pad.GetNetCode());b.Add(stub);b.Add(via);chosen={'target_mm':target,'distance_mm':dist,'offset_deg':delta};break
   records.append({'pad':f.GetReference()+'.'+pad.GetNumber(),'net':net,'attempts':attempts,'chosen':chosen,'foreign_copper_removed':0})
   print(name,records[-1],flush=True)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();p.SaveBoard(str(w/'main.kicad_pcb'),b)
(w/'service-landing-search.json').write_text(json.dumps(records,indent=2)+'\n')
