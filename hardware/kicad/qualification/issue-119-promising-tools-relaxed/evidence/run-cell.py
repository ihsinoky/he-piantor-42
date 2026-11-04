from common import *
import shutil
label,router=sys.argv[1:];assert label in ['main4','main2','smoke4','smoke2'];assert router in ['fab','krt','free']
gate=json.loads((E/'equivalence-gate.json').read_text());assert gate['pass_equivalence']
if label.startswith('main'):assert json.loads((E/'smoke-gate.json').read_text())['pass']
source=E/'inputs'/label
for filename,key in [('main.kicad_pcb','relaxed_pcb_sha256'),('corrected.dsn','relaxed_dsn_sha256'),('main.kicad_pro','relaxed_project_sha256')]:assert sha(source/filename)==gate['inputs'][label][key]
w=E/'runs'/label/router;w.mkdir(parents=True,exist_ok=False)
for ext in ['kicad_pcb','kicad_pro']:shutil.copyfile(source/f'main.{ext}',w/f'in.{ext}')
shutil.copyfile(source/'corrected.dsn',w/'corrected.dsn')
save(w/'launch.json',dict(utc=utc(),label=label,router=router,single_run=True,dimensions_mm=dict(width=.127,clearance=.127,via=.6,drill=.3)))
if router=='fab':
 rc=run(label+'-fab-route',[RT/'bun/bun-linux-x64/bun',E/'driver.ts',FAB,w/'corrected.dsn',w],timeout=1920)
elif router=='krt':
 args=['--escalation','off','--track-width','0.127','--clearance','0.127','--via-size','0.60','--via-drill','0.30','--layers','F.Cu','In1.Cu','In2.Cu','B.Cu','--layer-costs','1.0','-1','1.0','1.0']
 rc=run(label+'-krt-route',[R/'.issue113-runtime/venv/bin/python3','py_router/route.py',w/'in.kicad_pcb',w/'out.kicad_pcb']+args,cwd=KRT,timeout=1800)
else:
 t=Path('/home/hatch/workspace/tools/issue-93');java=next(t.glob('jdk-25*/bin/java'));jar=t/'freerouting-2.5.0.jar'
 assert sha(jar)=='f6f51bb02245e8e717f9359bd260cc9c5c0b1bc0acc8b7cb2cd5b8ffeb5de3c7'
 (w/'temp').mkdir();(w/'user-data').mkdir()
 args=[java,'-Djava.awt.headless=true','-Duser.language=en','-Duser.country=US','-Xmx2g',f'-Djava.io.tmpdir={w}/temp','-jar',jar,f'--user_data_path={w}/user-data','--gui.enabled=false','--api_server.enabled=false','-da','--profile.allow_telemetry=false','--router.automatic_neckdown=false','--router.max_threads=1','--router.optimizer.enabled=true','--router.fanout.enabled=true','--router.job_timeout=00:20:00','-mp','100','-mt','0','-is','sequential','-de',w/'corrected.dsn','-do',w/'out.ses']
 for key in list(os.environ):
  if key.startswith('FREEROUTING__'):os.environ.pop(key)
 env.update(LANG='C.UTF-8',LC_ALL='C.UTF-8',TZ='UTC')
 rc=run(label+'-free-route',args,cwd=w,timeout=1260)
save(w/'execution.json',dict(utc=utc(),exit_code=rc,outputs={p.name:sha(p) for p in w.iterdir() if p.is_file()},original_input_copy_unchanged=sha(w/'in.kicad_pcb')==sha(source/'main.kicad_pcb')))
assert rc==0
