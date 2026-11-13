"""Issue 233: independent native bottom-side placements, no mirrored board copper."""
from pathlib import Path
import pcbnew as p
import json,shutil,hashlib,sys,subprocess
E=Path(__file__).resolve().parent
BASE=E.parent/'issue-200-wing-rev3'
def save(f,o): f.write_text(json.dumps(o,indent=2)+'\n')
if len(sys.argv)==1:
 for name in sorted(BASE.glob('wing-rev3-*')):subprocess.run([sys.executable,__file__,name.name],check=True)
 sys.exit(0)
parents=[]
for src in sorted(BASE.glob('wing-rev3-*')):
 if src.name!=sys.argv[1]:continue
 w=E/src.name.replace('rev3','rev4');w.mkdir(exist_ok=True)
 b=p.LoadBoard(str(src/'input.kicad_pcb'));parents.append(b)
 for t in list(b.GetTracks()):b.Delete(t)
 for z in list(b.Zones()):
  if not z.GetIsRuleArea():b.Delete(z)
 spec=json.loads((src/'definition.json').read_text());spec['name']=w.name;spec['status']='Issue 233 study ONLY; not fabrication qualified'
 spec['schema_version']='wing-rev4-study-1'
 spec['harness']={'nominal_length_mm':200,'status':'D-033 remains unchanged; underside route NOT qualified; see ../case/summary.json'}
 spec['service_reservations']=[]
 spec['service_notes']=['All electronic parts and test pads on B.Cu; switches on top. Underside access requires Wing removal.']
 fs={f.GetReference():f for f in b.GetFootprints()};moved=[]
 for c in spec['components']:
  f=fs[c['reference']]
  if f.GetLayer()==p.F_Cu:
   # Flip the physical footprint at its own anchor, then restore the chosen
   # CCW board pose. Native pads preserve numbers/nets and change local chirality.
   f.Flip(f.GetPosition(),False)
   if c['reference']=='J_WING':c['rotation_ccw_deg']=(c['rotation_ccw_deg']+180)%360
   f.SetOrientationDegrees(c['rotation_ccw_deg'])
   c['side']='bottom';moved.append(c['reference'])
 assert all(fs[c['reference']].GetLayer()==p.B_Cu for c in spec['components'])
 for name in ('input.kicad_pro','main.kicad_pro'):shutil.copyfile(src/'input.kicad_pro',w/name)
 manager=p.GetSettingsManager();manager.LoadProject(str(w/'input.kicad_pro'));b.SetProject(manager.Prj())
 p.SaveBoard(str(w/'input.kicad_pcb'),b)
 save(w/'definition.json',spec);save(w/'placement-changes.json',{'moved_to_bottom':moved,'source':str(src.relative_to(E.parents[3])),'source_sha256':hashlib.sha256((src/'input.kicad_pcb').read_bytes()).hexdigest()})
 print(w.name,moved,flush=True)
