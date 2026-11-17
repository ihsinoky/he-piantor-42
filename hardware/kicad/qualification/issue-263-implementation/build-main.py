"""Main Rev.8: Rev.7 J2/J3 (GH side-entry) -> FH12 ZIF at the #261 poses.

Poses (case frame, #261 REPORT/audit): envelope centres J2-side
(-23.09,40.97) yaw +38, J3-side (+23.30,40.80) yaw -43; case = board -
(100,70) (verified from H1/H2/H3 hole correspondences, issue-228 dims).
Footprint origin (pad-row centre) = envelope centre + R(yaw)*(0,+1.40)
(housing centre at local y=+1.40, pad row at y=-1.00. KiCad file-frame rotation maps local (0,1) to (sin, -cos) of the orientation angle, so KiCad orientation = #261 case yaw, and origin = centre - (1.40 sin(yaw), -1.40 cos(yaw)) in file coords. Verified against built pad coordinates in pose-check.py.).
Assignment: pad n of each ZIF carries D-024 signal (15-n) - the cable's
k -> 15-k reversal is absorbed here (binding note, Issue #263 comment).
Verification from built pad coordinates follows in verify-main.py.
"""
from pathlib import Path
import pcbnew as p, json, math, shutil
E=Path(__file__).resolve().parent; BASE=E.parent/'issue-240-main-rev7'
FP='Hirose_FH12-14S-0.5SH_1x14-1MP_P0.50mm_Horizontal'
W=E/'main-rev8'; W.mkdir(exist_ok=True)
b=p.LoadBoard(str(BASE/'inspection/final/main.kicad_pcb'))
spec={'J2':dict(centre=(76.91,110.97),yaw=38.0),'J3':dict(centre=(123.30,110.80),yaw=-43.0)}
olds={}; oldfps={}
for f in b.GetFootprints():
 if f.GetReference() in spec:
  oldfps[f.GetReference()]=f
  olds[f.GetReference()]={a.GetNumber():a.GetNetCode() for a in f.Pads() if a.GetNumber() not in ('MP','15')}
  olds[f.GetReference()+'_names']={a.GetNetCode():a.GetNetname() for a in f.Pads() if a.GetNumber() not in ('MP','15')}
newfps={}
for ref in spec:
 f=p.FootprintLoad(str(E/'connector'),FP); assert f
 b.Add(f); newfps[ref]=f
info={}
for ref,s in spec.items():
 f=newfps[ref]; th=math.radians(s['yaw'])
 ox=s['centre'][0]-1.40*math.sin(th); oy=s['centre'][1]+1.40*math.cos(th)
 f.SetReference(ref); f.SetValue('FH12-14S-0.5SH(55)')
 f.SetPosition(p.VECTOR2I(round(ox*1e6),round(oy*1e6))); f.SetOrientationDegrees(s['yaw'])
 assign={}
 for a in f.Pads():
  if a.GetNumber()=='MP': a.SetNetCode(0)
  else:
   sig=str(15-int(a.GetNumber())); a.SetNetCode(olds[ref][sig]); assign[a.GetNumber()]=olds[ref+'_names'][olds[ref][sig]]
 info[ref]=dict(origin_mm=[ox,oy],yaw_deg=s['yaw'],envelope_centre_board_mm=list(s['centre']),assignment_pad_to_net=assign)
# Remove ANY kept copper colliding with the new pads (+0.10 mm): Rev.7
# copper (e.g. V5V2) passes under the FH12 fitting pads.
from shapely.geometry import box as sbox, LineString as SLine, Point as SPoint
padpolys=[]
for ref in ('J2','J3'):
 f=[x for x in b.GetFootprints() if x.GetReference()==ref][0]
 for a in f.Pads():
  padpolys.append(sbox(p.ToMM(a.GetPosition().x)-p.ToMM(a.GetSize().x)/2-.10,p.ToMM(a.GetPosition().y)-p.ToMM(a.GetSize().y)/2-.10,p.ToMM(a.GetPosition().x)+p.ToMM(a.GetSize().x)/2+.10,p.ToMM(a.GetPosition().y)+p.ToMM(a.GetSize().y)/2+.10))
collided=[]
for t in list(b.GetTracks()):
 if isinstance(t,p.PCB_VIA): g=SPoint(p.ToMM(t.GetPosition().x),p.ToMM(t.GetPosition().y)).buffer(p.ToMM(t.GetWidth(p.F_Cu))/2)
 else: g=SLine([(p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y)),(p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y))]).buffer(p.ToMM(t.GetWidth())/2,cap_style=1)
 if any(g.intersects(pp) for pp in padpolys): collided.append(t)
for t in collided: b.Remove(t)
print('removed colliding kept copper:',len(collided))
removed=0; netcodes=set()
for ref in spec: netcodes|=set(olds[ref].values())
for t in list(b.GetTracks()):
 if t.GetNetCode() not in netcodes: continue
 s,e=t.GetStart(),t.GetEnd()
 near=False
 for ref,sp in spec.items():
  cx,cy=sp['centre']
  if max(abs(p.ToMM(s.x)-cx),abs(p.ToMM(s.y)-cy))<22 and max(abs(p.ToMM(e.x)-cx),abs(p.ToMM(e.y)-cy))<22: near=True
 if near: b.Remove(t); removed+=1
for f in oldfps.values(): b.Remove(f)
p.SaveBoard(str(W/'input.kicad_pcb'),b)
src=BASE/'schematic/main.kicad_sch'
if src.exists(): shutil.copyfile(src,W/'main.kicad_sch')
(W/'swap.json').write_text(json.dumps(dict(removed_local_tracks=removed,sites=info),indent=2)+'\n')
print('main-rev8 input built; removed',removed)
