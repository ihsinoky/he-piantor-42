"""Case-frame pose verification of the as-built ZIFs vs #261 spec.

Wing: asm() transform from issue-228 dimensions (same as #235 pose
check). Envelope centre = pad-row centre + 2.40 mm toward the mouth
(mouth dir = pad-row centre -> MP centre). Spec: centre (+-27,-37.5),
entry slot (+-27,-34.2); pin index must increase toward +X on the
right, -X on the left (#264 transport convention).
Main: case = board - (100,70); envelope centres/yaws per #261.
"""
from pathlib import Path
import pcbnew as p, json, math
E=Path(__file__).resolve().parent; out={}
for w in sorted(E.glob('wing-rev5-*')):
 b=p.LoadBoard(str(w/'input.kicad_pcb')); f=[x for x in b.GetFootprints() if x.GetReference()=='J_WING'][0]
 d=json.loads((w/'definition.json').read_text()); side=w.name.split('-')[-1]
 dims=json.loads((E.parents[3]/f'hardware/case/issue-228-final/{int(d["pitch_mm"])}mm/dimensions.json').read_text())
 tr=dims['wing_transforms'][side]; m=tr['matrix']; t=tr['translation']
 def asm(pos):
  x,y=p.ToMM(pos.x)-100,100-p.ToMM(pos.y); return [m[0][0]*x+m[0][1]*y+t[0],m[1][0]*x+m[1][1]*y+t[1]]
 pads={a.GetNumber():asm(a.GetPosition()) for a in f.Pads()}
 row=[pads[str(k)] for k in range(1,15)]; rc=[sum(q[0] for q in row)/14,sum(q[1] for q in row)/14]
 mp=[pads['MP']] if 'MP' in pads else []
 mps=[asm(a.GetPosition()) for a in f.Pads() if a.GetNumber()=='MP']; mc=[sum(q[0] for q in mps)/2,sum(q[1] for q in mps)/2]
 dvec=[mc[0]-rc[0],mc[1]-rc[1]]; L=math.hypot(*dvec); u=[dvec[0]/L,dvec[1]/L]
 centre=[rc[0]+2.40*u[0],rc[1]+2.40*u[1]]; mouth=[centre[0]+3.20*u[0],centre[1]+3.20*u[1]]
 idx=[pads['14'][0]-pads['1'][0],pads['14'][1]-pads['1'][1]]
 out[w.name]=dict(envelope_centre_case=[round(v,3) for v in centre],mouth_case=[round(v,3) for v in mouth],
  pin1_case=[round(v,3) for v in pads['1']],pin14_case=[round(v,3) for v in pads['14']],
  index_dir_x=round(idx[0],3))
b=p.LoadBoard(str(E/'main-rev8/input.kicad_pcb'))
for ref in ('J2','J3'):
 f=[x for x in b.GetFootprints() if x.GetReference()==ref][0]
 pads={a.GetNumber():[p.ToMM(a.GetPosition().x)-100,p.ToMM(a.GetPosition().y)-70] for a in f.Pads()}
 out['main-'+ref]=dict(pin1_case=[round(v,3) for v in pads['1']],pin14_case=[round(v,3) for v in pads['14']],
  origin_case=[round(p.ToMM(f.GetPosition().x)-100,3),round(p.ToMM(f.GetPosition().y)-70,3)],yaw_kicad=f.GetOrientationDegrees())
(E/'pose-verification.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=1)[:1200])
