from common import *
import shutil
label=sys.argv[1];stage,cell=label.split('-');c=json.loads((E/'conditions.json').read_text())[cell]
gate=json.loads((E/'equivalence-gate.json').read_text());assert gate['pass_equivalence'];source=E/'inputs'/label
for f,h in gate['inputs'][label]['hashes'].items():assert sha(source/f)==h
if stage=='main':assert json.loads((E/'smoke-gates'/(cell+'.json')).read_text())['pass']
w=E/'runs'/label/'krt';w.mkdir(parents=True,exist_ok=False)
for ext in ['kicad_pcb','kicad_pro']:shutil.copyfile(source/f'main.{ext}',w/f'in.{ext}')
save(w/'launch.json',dict(utc=utc(),label=label,single_run=True,condition=c))
rc=run(label+'-krt-route',[R/'.issue113-runtime/venv/bin/python3','py_router/route.py',w/'in.kicad_pcb',w/'out.kicad_pcb']+c['args'],cwd=KRT,timeout=1800)
save(w/'execution.json',dict(utc=utc(),exit_code=rc,outputs={p.name:sha(p) for p in w.iterdir() if p.is_file()},original_input_copy_unchanged=sha(w/'in.kicad_pcb')==sha(source/'main.kicad_pcb')))
assert rc==0
