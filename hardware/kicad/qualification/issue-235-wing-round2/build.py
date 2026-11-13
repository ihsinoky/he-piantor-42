"""One bounded placement trial per variant; fixed geometry from round 1."""
from pathlib import Path
import pcbnew as p
import json,shutil,math,sys,subprocess,subprocess
E=Path(__file__).resolve().parent;BASE=E.parent/'issue-233-wing-single-sided'
V=lambda x,y:p.VECTOR2I(round(x*1e6),round(y*1e6))
if len(sys.argv)==1:
 for src in sorted(BASE.glob('wing-rev4-*')):subprocess.run([sys.executable,__file__,src.name],check=True)
 sys.exit(0)
if len(sys.argv)==1:
 for src in sorted(BASE.glob('wing-rev4-*')):subprocess.run([sys.executable,__file__,src.name],check=True)
 sys.exit(0)
parents=[]
for src in sorted(BASE.glob('wing-rev4-*')):
 if src.name!=sys.argv[1]:continue
 if src.name!=sys.argv[1]:continue
 w=E/src.name;w.mkdir(exist_ok=True);b=p.LoadBoard(str(src/'input.kicad_pcb'));parents.append(b)
 d=json.loads((src/'definition.json').read_text());d['status']='Issue 235 round 2 diagnostic; no manufacturing release';d['schema_version']='wing-rev4-study-2'
 fs={f.GetReference():f for f in b.GetFootprints()};cs={c['reference']:c for c in d['components']}
 dims=json.loads((E.parents[3]/f'hardware/case/issue-228-final/{int(d["pitch_mm"])}mm/dimensions.json').read_text());tr=dims['wing_transforms'][w.name.split('-')[-1]];m=tr['matrix']
 changes=[]
 for g in 'ABC':
  c=cs['U_MUX_'+g];cap=cs['C_MUX_'+g];ox,oy=c['x_mm'],c['y_mm']
  # Move the service row 2 mm south in assembly coordinates, and rotate 180.
  dx,dy=m[1][0]*2,m[1][1]*2
  for cc in (c,cap):
   if cc is cap:cc['x_mm'],cc['y_mm']=2*ox-cc['x_mm'],2*oy-cc['y_mm']
   cc['x_mm']+=dx;cc['y_mm']+=dy;cc['rotation_ccw_deg']=(cc['rotation_ccw_deg']+180)%360
   f=fs[cc['reference']];f.SetPosition(V(100+cc['x_mm'],100-cc['y_mm']));f.SetOrientationDegrees(cc['rotation_ccw_deg']);changes.append(cc['reference'])
 old=fs['J_WING'];c=cs['J_WING'];nets={a.GetNumber():a.GetNetCode() for a in old.Pads()};pos=old.GetPosition();angle=old.GetOrientationDegrees();c['rotation_ccw_deg']=angle
 f=p.FootprintLoad(str(E/'connector'),'JST_GH_SM14B-GHS-TB_1x14-1MP_P1.25mm_Horizontal');assert f
 b.Add(f);f.SetReference('J_WING');f.SetValue('SM14B-GHS-TB(LF)(SN)');f.Flip(f.GetPosition(),False);f.SetPosition(pos);f.SetOrientationDegrees(angle)
 for a in f.Pads():a.SetNetCode(nets[a.GetNumber()])
 b.Remove(old);c['mpn']=f.GetValue();c['value']=f.GetValue();c['kind']='connector_ra'
 for n in ('input.kicad_pro','main.kicad_pro'):shutil.copyfile(src/'input.kicad_pro',w/n)
 p.SaveBoard(str(w/'input.kicad_pcb'),b)
 (w/'definition.json').write_text(json.dumps(d,indent=2)+'\n');(w/'placement-changes.json').write_text(json.dumps({'moved':changes,'mux_rotation_delta_deg':180,'mux_assembly_delta_mm':[0,2],'connector_anchor_and_angle_invariant':True},indent=2)+'\n')
 print(w.name,flush=True)
