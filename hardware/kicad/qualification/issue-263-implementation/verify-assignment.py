"""Position-space pin-assignment verification (Issue #263, #252 method).

Lanes are tracked by CASE-FRAME POSITION, not pad numbers: Wing pads
sorted by projection on the #264 transport lateral axis s0 give the
lane order; the 5-fold transport reverses lateral order (recomputed
from #264 headings); Main pads sorted by projection on sref must carry
the same D-024 signal at the mirrored index. Signal identity: Wing net
names via the Wing definition (pad k = signal k), Main net names via
Rev.7's J2/J3 pad map (pad k carried signal k). Pad coordinates are
read from the BUILT boards and recorded.
"""
from pathlib import Path
import pcbnew as p, json, math
E=Path(__file__).resolve().parent
def tvec(phi):
 r=math.radians(phi); return (math.sin(r),math.cos(r))
def reflect(v,f):
 d=v[0]*f[0]+v[1]*f[1]; return (2*d*f[0]-v[0],2*d*f[1]-v[1])
def fold_line(tin,tout):
 sx,sy=tin[0]+tout[0],tin[1]+tout[1]; n=math.hypot(sx,sy)
 return (-tin[1],tin[0]) if n<1e-6 else (sx/n,sy/n)
def transport(heads):
 t0=tvec(heads[0]); s=(t0[1],-t0[0])
 for i in range(len(heads)-1): s=reflect(s,fold_line(tvec(heads[i]),tvec(heads[i+1])))
 tf=tvec(heads[-1]); sref=(tf[1],-tf[0]); return s,(s[0]*sref[0]+s[1]*sref[1]),sref
# #264 headings are in a y-north math frame; case frame is y-south:
# convert a lateral axis (x,y)_ynorth -> (x,-y)_case.
def case_axis(v): return (v[0],-v[1])
def pads_case(board,ref,to_case):
 b=p.LoadBoard(str(board)); f=[x for x in b.GetFootprints() if x.GetReference()==ref][0]
 return [(a.GetNumber(),a.GetNetname(),to_case(p.ToMM(a.GetPosition().x),p.ToMM(a.GetPosition().y))) for a in f.Pads() if a.GetNumber() not in ('MP','15')]
def wing_case(w):
 d=json.loads((w/'definition.json').read_text()); side=w.name.split('-')[-1]
 dims=json.loads((E.parents[3]/f'hardware/case/issue-228-final/{int(d["pitch_mm"])}mm/dimensions.json').read_text())
 tr=dims['wing_transforms'][side]; m=tr['matrix']; t=tr['translation']
 return lambda bx,by: (m[0][0]*(bx-100)+m[0][1]*(100-by)+t[0], m[1][0]*(bx-100)+m[1][1]*(100-by)+t[1])
out={'sides':{}}; ok=True
rev7={ref:None for ref in ('J2','J3')}
b7=p.LoadBoard(str(E.parent/'issue-240-main-rev7/inspection/final/main.kicad_pcb'))
sig_of={}
for ref in ('J2','J3'):
 f=[x for x in b7.GetFootprints() if x.GetReference()==ref][0]
 sig_of[ref]={a.GetNetname():int(a.GetNumber()) for a in f.Pads() if a.GetNumber() not in ('MP','15')}
for side,wingdir,mainref,heads in [('right','wing-rev5-17mm-right','J3',[-4.4,-116.9,2.66,-177.34,2.66,43.0]),
                                    ('left','wing-rev5-17mm-left','J2',[4.4,116.9,-2.66,177.34,-2.66,-38.0]),
                                    ('right16','wing-rev5-16mm-right','J3',[-4.4,-116.9,2.66,-177.34,2.66,43.0]),
                                    ('left16','wing-rev5-16mm-left','J2',[4.4,116.9,-2.66,177.34,-2.66,-38.0])]:
 s0,dot,sref=transport(heads); assert dot<0
 s0c,srefc=case_axis(s0),case_axis(sref)
 w=pads_case(E/wingdir/'input.kicad_pcb','J_WING',wing_case(E/wingdir))
 wdef=json.loads((E/wingdir/'definition.json').read_text())
 wsig={c['reference']:c for c in wdef['components']}
 wing_sig={num:int(num) for num,net,pos in w}  # Wing pad k carries D-024 signal k (definition pins)
 wsorted=sorted(w,key=lambda r: r[2][0]*s0c[0]+r[2][1]*s0c[1])
 m=pads_case(E/'main-rev8/input.kicad_pcb',mainref,lambda bx,by:(bx-100,by-70))
 msorted=sorted(m,key=lambda r: r[2][0]*srefc[0]+r[2][1]*srefc[1])
 rows=[]
 for i,(wnum,wnet,wpos) in enumerate(wsorted):
  mnum,mnet,mpos=msorted[13-i]
  expected_sig=wing_sig[wnum]
  got_sig=sig_of[mainref].get(mnet)
  good=(mnet=='GND' and wnet=='GND') or got_sig==expected_sig
  ok&=good
  rows.append(dict(lane=i,wing_pad=wnum,wing_net=wnet,wing_case=[round(v,2) for v in wpos],
                   main_pad=mnum,main_net=mnet,main_case=[round(v,2) for v in mpos],
                   signal=expected_sig,match=good))
 out['sides'][side]=dict(s0_case=[round(v,3) for v in s0c],sref_case=[round(v,3) for v in srefc],rows=rows)
out['pass']=bool(ok)
(E/'main-rev8/assignment-verification.json').write_text(json.dumps(out,indent=2)+'\n')
print('position-space assignment verification pass:',ok)
