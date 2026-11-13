"""Native flip/rotation of physical front/rear/exit probes, not hand-derived signs."""
from pathlib import Path
import pcbnew as p
import json,math
E=Path(__file__).resolve().parent;records=[];keep=[]
V=lambda x,y:p.VECTOR2I(round(x*1e6),round(y*1e6))
for w in sorted(E.glob('wing-rev4-*')):
 b=p.LoadBoard(str(w/'input.kicad_pcb'));keep.append(b);f=next(f for f in b.GetFootprints() if f.GetReference()=='J_WING');d=json.loads((w/'definition.json').read_text());side=w.name.split('-')[-1];sgn=-1 if side=='left' else 1
 dims=json.loads((E.parents[3]/f'hardware/case/issue-228-final/{int(d["pitch_mm"])}mm/dimensions.json').read_text());tr=dims['wing_transforms'][side];m=tr['matrix'];t=tr['translation']
 def asm(pos):
  x,y=p.ToMM(pos.x)-100,100-p.ToMM(pos.y);return [m[0][0]*x+m[0][1]*y+t[0],m[1][0]*x+m[1][1]*y+t[1]]
 probe_board=p.BOARD();probe=p.FootprintLoad(str(E/'connector'),'JST_GH_SM14B-GHS-TB_1x14-1MP_P1.25mm_Horizontal');probe_board.Add(probe);keep.extend([probe_board,probe])
 pads={}
 for key,y in [('rear',-1.6),('face',2.45),('wire_exit',5.55)]:
  a=p.PAD(probe);a.SetNumber(key);a.SetPosition(V(0,y));probe.Add(a);pads[key]=a
 probe.Flip(probe.GetPosition(),False);probe.SetPosition(f.GetPosition());probe.SetOrientationDegrees(f.GetOrientationDegrees())
 world={key:asm(a.GetPosition()) for key,a in pads.items()}
 for key,y in [('rear',-42.6),('face',-38.55),('wire_exit',-35.45)]:assert math.dist(world[key],[sgn*27,y])<.000003,(w.name,key,world[key])
 world['pin1']=asm(next(a for a in f.Pads() if a.GetNumber()=='1').GetPosition());world['pin14']=asm(next(a for a in f.Pads() if a.GetNumber()=='14').GetPosition())
 records.append({'variant':w.name,'native_orientation_deg':f.GetOrientationDegrees(),'case_xy_mm':world,'native_transformed_probes_pass':True})
(E/'connector/placement.json').write_text(json.dumps(records,indent=2)+'\n');print('Native connector front/rear/exit probes pass',len(records))
