"""Two bounded whole-board attempts from independently prepared seeds; no local repair."""
from common import *
import shutil
label=sys.argv[1];assert label in ['seed-a','seed-b']
source=E/'inputs'/label;w=E/'runs'/label
# Added after the recorded two runs: future callers must stop on failed input DRC.
# No third run is allowed in Issue169, including a run through this repaired guard.
assert len(list((E/'runs').glob('seed-*/execution.json')))<2, 'Issue169 whole-board attempt budget exhausted'
preflight=E/('preflight-4.json' if label=='seed-a' else 'preflight-seed-b-revision2.json')
violations=json.loads(preflight.read_text())['violations']
assert not [v for v in violations if v['type'] not in {'text_height','silk_overlap','silk_over_copper','via_dangling'}], 'Input copper preflight failed'
w.mkdir(parents=True,exist_ok=False)
args=ARGS+['--keep-input-copper']
if label=='seed-b':args+=['--ordering','inside_out','--direction','backward']
for ext in ['kicad_pcb','kicad_pro']:shutil.copyfile(source/('main.'+ext),w/('in.'+ext))
assert run(label+'-effective',[B/'venv/bin/python3',E/'read-effective.py',w/'effective.json',source/'main.kicad_pcb']+args)==0
read=json.loads((w/'effective.json').read_text());c=read['grid_route_config']
assert c['track_width']==.1 and c['clearance']==.1 and c['via_size']==.6 and c['via_drill']==.3 and c['layer_costs']==[1.,-1.,1.,1.]
assert read['escalation_policy'][0]=='off' and len(read['native_keepouts'])==4
save(w/'input-hashes.json',{str(x.relative_to(E)):digest(x) for x in source.iterdir() if x.is_file()})
rc=run(label+'-krt-route',[B/'venv/bin/python3','py_router/route.py',w/'in.kicad_pcb',w/'out.kicad_pcb']+args,cwd=K,timeout=2400)
save(w/'execution.json',dict(utc=now(),whole_board_attempt=1 if label=='seed-a' else 2,exit_code=rc,condition_args=args,input_unchanged=digest(w/'in.kicad_pcb')==digest(source/'main.kicad_pcb')))
raise SystemExit(rc)
