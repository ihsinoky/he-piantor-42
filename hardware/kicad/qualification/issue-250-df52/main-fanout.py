"""Explicit DF52 solder-tail fanout for the unresolved MUX_OUT_B branch."""
from pathlib import Path
import pcbnew as p,json,math,shutil
E=Path(__file__).resolve().parent;T=E.parents[3]/'.issue250-runtime';w=E/'main';b=p.LoadBoard(str(w/'main.kicad_pcb'));held=[];changes=[]
tracks=list(b.GetTracks());feet=list(b.GetFootprints());pads=[a for f in feet for a in f.Pads()]
from verify import polys
from shapely.geometry import Point,LineString
areas=[(polys(z.Outline()),set(z.GetLayerSet().Seq())) for z in list(b.Zones())+[z for f in feet for z in f.Zones()] if z.GetIsRuleArea()]
def xy(v):return [p.ToMM(v.x),p.ToMM(v.y)]
def clear(start,end,net):
 sh=p.SHAPE_SEGMENT(start,end,100000);vshape=p.SHAPE_CIRCLE(end,300000)
 if any(p.F_Cu in ls and LineString([xy(start),xy(end)]).buffer(.05).intersects(g) for g,ls in areas):return False
 for a in pads:
  for l in b.GetEnabledLayers().CuStack():
   if a.IsOnLayer(l) and a.GetEffectiveShape(l).Distance(end)<425001:return False
  if a.IsOnLayer(p.F_Cu) and a.GetNetname()!=net and a.GetEffectiveShape(p.F_Cu).Collide(sh,100001):return False
 for t in tracks:
  if t.GetNetname()==net:continue
  ls=list(b.GetEnabledLayers().CuStack()) if isinstance(t,p.PCB_VIA) else [t.GetLayer()]
  shape=p.SHAPE_CIRCLE(t.GetPosition(),300000) if isinstance(t,p.PCB_VIA) else p.SHAPE_SEGMENT(t.GetStart(),t.GetEnd(),t.GetWidth())
  if isinstance(t,p.PCB_VIA):g=Point(xy(t.GetPosition())).buffer(.3)
  else:g=LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2)
  if g.distance(Point(xy(end)))<.400001:return False
  if p.F_Cu in ls and sh.Collide(shape,100001):return False
 return True
for t in b.GetTracks():
 if t.GetNetname()=='MUX_OUT_B':held.append(t);b.Remove(t)
for f in b.GetFootprints():
 if f.GetReference() not in ('J2','J3'):continue
 a=next(a for a in f.Pads() if a.GetNumber()=='11');ang=math.radians(f.GetOrientationDegrees());chosen=None
 for d in [-.8,-.9,-1.,-1.1,-1.2,-1.3,-1.4,-1.5,-1.75,-2.,-2.5,-3.,-3.5,-4.,-5.,-6.]:
  for du in [0,.25,-.25,.5,-.5,.75,-.75,1.,-1.,1.5,-1.5,2.,-2.,3.,-3.]:
   pos=p.VECTOR2I(a.GetPosition().x+p.FromMM(du*math.cos(ang)+d*math.sin(ang)),a.GetPosition().y+p.FromMM(-du*math.sin(ang)+d*math.cos(ang)))
   if clear(a.GetPosition(),pos,a.GetNetname()):chosen=(du,d,pos);break
  if chosen:break
 if not chosen:raise RuntimeError('No straight fanout for '+f.GetReference())
 du,d,pos=chosen
 v=p.PCB_VIA(b);v.SetPosition(pos);v.SetWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNetCode(a.GetNetCode());b.Add(v)
 t=p.PCB_TRACK(b);t.SetStart(a.GetPosition());t.SetEnd(pos);t.SetLayer(p.F_Cu);t.SetWidth(p.FromMM(.1));t.SetNetCode(a.GetNetCode());b.Add(t)
 changes.append(dict(ref=f.GetReference(),pin='11',fanout_local_delta_mm=[du,d],via_mm=[p.ToMM(pos.x),p.ToMM(pos.y)]))
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(T/'main-fanout-input.kicad_pcb'),b);shutil.copyfile(w/'main.kicad_pro',T/'main-fanout-input.kicad_pro');(E/'main/fanout.json').write_text(json.dumps(changes,indent=2)+'\n')
