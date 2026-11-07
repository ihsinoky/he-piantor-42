"""Choose a native-pad-safe GND escape landing inside the main back pour.
Minimize displaced signal copper; escape-pad logs every displacement. Full
repair/DRC/graph qualification is mandatory afterwards.
"""
from pathlib import Path
import sys,math,json,subprocess
import pcbnew as p
from shapely.geometry import Point,LineString
from shapely.ops import unary_union
from verify import xy,polys
E=Path(__file__).resolve().parent;name=sys.argv[1];w=E/name;b=p.LoadBoard(str(w/'main.kicad_pcb'))
f=next(f for f in b.GetFootprints() if f.GetReference()=='U_MUX_B');a=next(a for a in f.Pads() if a.GetNumber()=='14');origin=xy(a.GetPosition());net='GND'
planes=unary_union([polys(z.GetFilledPolysList(p.B_Cu)) for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname()==net and z.IsOnLayer(p.B_Cu)])
parts=list(planes.geoms) if hasattr(planes,'geoms') else [planes];core=max(parts,key=lambda q:q.area).buffer(-.31)
pads=[(aa,{l:aa.GetEffectiveShape(l) for l in (p.F_Cu,p.B_Cu) if aa.IsOnLayer(l)}) for f in b.GetFootprints() for aa in f.Pads() if aa.GetAttribute()!=p.PAD_ATTRIB_NPTH];candidates=[]
for rs in range(12,91):
 radius=rs*.05
 for angle in range(0,360,5):
  target=[origin[0]+radius*math.cos(math.radians(angle)),origin[1]+radius*math.sin(math.radians(angle))];pos=p.VECTOR2I(round(target[0]*1e6),round(target[1]*1e6));target=xy(pos);point=Point(target)
  if not core.contains(point):continue
  if any(s.Distance(pos)/1e6-.3<.135 for _,ss in pads for s in ss.values()):continue
  stub=p.SHAPE_SEGMENT(a.GetPosition(),pos,300000)
  if any(aa.GetNetname()!=net and p.F_Cu in ss and ss[p.F_Cu].Collide(stub,110000) for aa,ss in pads):continue
  line=LineString([origin,target]).buffer(.15);disk=point.buffer(.3);rips=0
  for t in b.GetTracks():
   if t.GetNetname()==net:continue
   geom=Point(xy(t.GetPosition())).buffer(.3) if isinstance(t,p.PCB_VIA) else LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2)
   if geom.distance(disk)<.10001 or (t.IsOnLayer(p.F_Cu) and geom.distance(line)<.10001):rips+=1
  candidates.append((rips,radius,target))
assert candidates,'no main-pour escape candidate'
rips,radius,target=min(candidates)
subprocess.run([sys.executable,str(E/'escape-pad.py'),name,'U_MUX_B','14',str(target[0]),str(target[1])],check=True)
(w/'ground-rescue-complete.json').write_text(json.dumps(dict(target_mm=target,expected_rips=rips,main_ground_landing=True))+'\n')
