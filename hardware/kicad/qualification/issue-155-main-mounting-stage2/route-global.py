"""Single global attempt, final permitted routing attempt in this task."""
from common import *
import shutil
source=E/'inputs/global';w=E/'runs/global';w.mkdir(parents=True,exist_ok=False)
assert (E/'global-scope.json').exists()
for ext in ['kicad_pcb','kicad_pro']:shutil.copyfile(source/('main.'+ext),w/('in.'+ext))
args=ARGS+['--keep-input-copper']
assert run('global-effective',[B/'venv/bin/python3',E/'read-effective.py',w/'effective.json',source/'main.kicad_pcb']+args)==0
read=json.loads((w/'effective.json').read_text());c=read['grid_route_config']
assert c['track_width']==.1 and c['clearance']==.1 and c['via_size']==.6 and c['via_drill']==.3 and c['layer_costs']==[1.,-1.,1.,1.]
assert read['escalation_policy'][0]=='off'
assert len(read['native_keepouts'])==4
assert all(set(x['layers'])=={'F.Cu','In1.Cu','In2.Cu','B.Cu'} and not x['tracks_allowed'] and not x['vias_allowed'] and not x['copper_pour_allowed'] and x['pads_allowed'] for x in read['native_keepouts'])
save(w/'effective-condition-audit.json',dict(utc=now(),pass_gate=True,conditions=c,keepouts=read['native_keepouts'],retain_input_copper=True))
rc=run('global-krt-route',[B/'venv/bin/python3','py_router/route.py',w/'in.kicad_pcb',w/'out.kicad_pcb']+args,cwd=K,timeout=1800)
save(w/'execution.json',dict(utc=now(),attempt=1,final_routing_attempt=True,exit_code=rc,condition_args=args,input_copy_unchanged=digest(w/'in.kicad_pcb')==digest(source/'main.kicad_pcb'),outputs={x.name:digest(x) for x in w.iterdir() if x.is_file()}))
assert rc==0
