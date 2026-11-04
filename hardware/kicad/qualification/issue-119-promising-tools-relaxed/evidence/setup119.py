from pathlib import Path
import subprocess,json,shutil,datetime
R=Path.cwd();Q=R/'hardware/kicad/qualification';E=Q/'issue-119-promising-tools-relaxed/evidence';E.mkdir(parents=True)
git=['git','--git-dir=/tmp/issue-119-main/git'];ref=subprocess.check_output(git+['rev-parse','origin/issue-117-four-layer-main'],text=True).strip()
old='hardware/kicad/qualification/issue-117-four-layer-main/evidence/'
# Read all reused source material directly from the pending GitHub branch, not local untracked files.
paths=subprocess.check_output(git+['ls-tree','-r','--name-only',ref,old],text=True).splitlines()
for f in paths:
 rel=f[len(old):]
 if rel.startswith(('inputs/main/','amendment-01/inputs/smoke-02/')) or rel.endswith(('.py','.ts')) or rel in ['native-equivalence.json','dsn-equivalence.json','preparation-readback.json','amendment-01/main-reuse-and-runtime-revalidation.json']:
  p=E/'source-117'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(subprocess.check_output(git+['show',ref+':'+f]))
shutil.copy('/tmp/issue-119-main/issue119.json',E/'issue119.json')
shutil.copy('/home/hatch/workspace/goals/he-piantor-42-keyboard-pmo/instructions/issue-119-promising-tools-relaxed.md',E/'instructions.md')
(E/'start.json').write_text(json.dumps(dict(start_utc='2026-11-04T09:58:00+00:00',stage0_deadline_utc='2026-11-04T10:58:00+00:00',deadline_utc='2026-11-04T12:58:00+00:00',source117_commit=ref,base_commit=subprocess.check_output(git+['rev-parse','origin/main'],text=True).strip()),indent=2)+'\n')
s=(E/'source-117/common.py').read_text().replace("GIT='/tmp/issue-117-main/git'","GIT='/tmp/issue-119-main/git'").replace("'/tmp/issue-117-main/'","'/tmp/issue-119-main/'")
(E/'common.py').write_text(s)
(E/'helpers.py').write_text('from common import *\nA=E\n')
shutil.copy(E/'source-117/amendment-01/driver.ts',E/'driver.ts')
# Inspectors take an explicit condition label (main4, smoke4, main2, smoke2).
s=(E/'source-117/amendment-01/read-refill.py').read_text();start=s.index('stage,router=');end=s.index('manager=p.GetSettingsManager()')
s=s[:start]+"label,router=sys.argv[1:];source=E/'inputs'/label\nraw=E/'runs'/label/router;w=E/'inspection'/label/router;w.mkdir(parents=True,exist_ok=False)\n"+s[end:]
s=s.replace("if router=='fab':","if router in ['fab','free']:")
s=s.replace("tracks={};widths={};vias={}","tracks={b.GetLayerName(i):0 for i in b.GetEnabledLayers().CuStack()};widths={};vias={}")
(E/'read-refill.py').write_text(s)
s=(E/'source-117/amendment-01/independent-check.py').read_text();start=s.index('stage,router=');end=s.index('def children(')
s=s[:start]+'''label,router=sys.argv[1:];stage='main' if label.startswith('main') else 'smoke'
source=E/'inputs'/label;raw=E/'runs'/label/router;w=E/'inspection'/label/router
assert run(label+'-'+router+'-refill',['/usr/bin/python3',E/'read-refill.py',label,router])==0
assert run(label+'-'+router+'-snapshot',['/usr/bin/python3',R/'hardware/kicad/qualification/eda-004g/resume-02/read-pcb.py',w/'main.kicad_pcb',w/'snapshot.json'])==0
assert run(label+'-'+router+'-drc',[RT/'kicad/usr/bin/kicad-cli','pcb','drc','--format','json','--severity-all','-o',w/'drc.json',w/'main.kicad_pcb'])==0
'''+s[end:]
s=s.replace('float(k)>=.2','float(k)>=.127').replace("plane_pass=physical['In1_signal_tracks']==0 and len(physical['zones'])==1 and physical['zones'][0]['filled'] and physical['zones'][0]['net']==('GND' if stage=='main' else 'N')","plane_pass=(not physical['zones']) if label.endswith('2') else (physical['In1_signal_tracks']==0 and len(physical['zones'])==1 and physical['zones'][0]['filled'] and physical['zones'][0]['net']==('GND' if stage=='main' else 'N'))")
(E/'independent-check.py').write_text(s)
print(E)
