from helpers import *
import shutil
stage,router=sys.argv[1:3];attempt=sys.argv[3] if len(sys.argv)>3 else '01'
label=stage if attempt=='01' else stage+'-'+attempt
assert stage in ['smoke','main'] and router in ['fab','krt']
assert json.loads((A/('equivalence-gate.json' if attempt=='01' else 'equivalence-gate-02.json')).read_text())['pass_equivalence']
if stage=='main':assert json.loads((A/'smoke-gate.json').read_text())['pass']
source=(E if stage=='main' else A)/'inputs'/label
if stage=='main':
 for path,row in json.loads((A/'main-reuse-and-runtime-revalidation.json').read_text())['files'].items():assert sha(E/path)==row['sha256']
w=A/'runs'/label/router;w.mkdir(parents=True,exist_ok=False)
for ext in ['kicad_pcb','kicad_pro']:shutil.copyfile(source/f'main.{ext}',w/f'in.{ext}')
shutil.copyfile(source/'corrected.dsn',w/'corrected.dsn')
save(w/'launch.json',dict(utc=utc(),stage=stage,router=router,input_sha256=sha(w/'in.kicad_pcb'),dsn_sha256=sha(w/'corrected.dsn'),project_sha256=sha(w/'in.kicad_pro'),single_run=True,dimensions_mm=dict(width=.2,clearance=.2,via=.6,drill=.3)))
if router=='fab':
 rc=run('amend01-'+label+'-fab-route',[RT/'bun/bun-linux-x64/bun',A/'driver.ts',FAB,w/'corrected.dsn',w],timeout=1920)
else:
 args=['--escalation','off','--track-width','0.20','--clearance','0.20','--via-size','0.60','--via-drill','0.30','--layers','F.Cu','In1.Cu','In2.Cu','B.Cu','--layer-costs','1.0','-1','1.0','1.0']
 rc=run('amend01-'+label+'-krt-route',[R/'.issue113-runtime/venv/bin/python3','py_router/route.py',w/'in.kicad_pcb',w/'out.kicad_pcb']+args,cwd=KRT,timeout=1800)
save(w/'execution.json',dict(utc=utc(),exit_code=rc,outputs={p.name:sha(p) for p in w.iterdir() if p.is_file()},original_input_copy_unchanged=sha(w/'in.kicad_pcb')==sha(source/'main.kicad_pcb')))
assert rc==0
