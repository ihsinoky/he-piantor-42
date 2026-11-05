"""Single local routing attempt with pinned D-019 settings; no retries."""
from common import *
import shutil
assert json.loads((E/'equivalence-gate.json').read_text())['pass_gate']
source=E/'inputs/local';w=E/'runs/local';w.mkdir(parents=True,exist_ok=False)
for ext in ['kicad_pcb','kicad_pro']:shutil.copyfile(source/('main.'+ext),w/('in.'+ext))
assert run('local-effective',[B/'venv/bin/python3',E/'read-effective.py',w/'effective.json',source/'main.kicad_pcb']+ARGS)==0
read=json.loads((w/'effective.json').read_text());config=read['grid_route_config']
save(w/'effective-condition-audit.json',dict(utc=now(),config=config,escalation_policy=read['escalation_policy']))
assert config['track_width']==.1 and config['clearance']==.1 and config['via_size']==.6 and config['via_drill']==.3
# Native rule areas are always parsed by KRT (not the optional user-layer keepout switch).
assert run('local-krt-route',[B/'venv/bin/python3','py_router/route.py',w/'in.kicad_pcb',w/'out.kicad_pcb']+ARGS,cwd=K,timeout=1800)==0
save(w/'execution.json',dict(utc=now(),attempt=1,condition_args=ARGS,input_copy_unchanged=digest(w/'in.kicad_pcb')==digest(source/'main.kicad_pcb'),output_hashes={x.name:digest(x) for x in w.iterdir() if x.is_file()}))
