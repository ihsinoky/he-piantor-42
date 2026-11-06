"""One authorized whole-board attempt; fail closed on preflight or repeat calls.

Uses the repaired Issue169 preflight predicate. A hash-bound receipt and atomic
attempt reservation also prevent stale DRC or retry after a killed process.
"""
from common import *
import shutil
source=E/'inputs/final';w=E/'runs/final'
assert not (E/'attempt-reserved.json').exists(), 'Issue173 whole-board attempt budget exhausted'
receipt=json.loads((E/'preflight-receipt.json').read_text())
assert receipt['pass_preflight']
assert receipt['board_sha256']==digest(source/'main.kicad_pcb')
assert receipt['project_sha256']==digest(source/'main.kicad_pro')
assert receipt['drc_sha256']==digest(E/'preflight.json')
violations=json.loads((E/'preflight.json').read_text())['violations']
assert not [v for v in violations if v['type'] not in {'text_height','silk_overlap','silk_over_copper','via_dangling'}], 'Input copper preflight failed'
w.mkdir(parents=True,exist_ok=False)
args=ARGS+['--keep-input-copper']
for ext in ['kicad_pcb','kicad_pro']:shutil.copyfile(source/('main.'+ext),w/('in.'+ext))
assert run('final-effective',[B/'venv/bin/python3',E/'read-effective.py',w/'effective.json',source/'main.kicad_pcb']+args)==0
read=json.loads((w/'effective.json').read_text());c=read['grid_route_config']
assert c['track_width']==.1 and c['clearance']==.1 and c['via_size']==.6 and c['via_drill']==.3 and c['layer_costs']==[1.,-1.,1.,1.]
assert read['escalation_policy'][0]=='off' and len(read['native_keepouts'])==4
save(w/'input-hashes.json',{str(x.relative_to(E)):digest(x) for x in source.iterdir() if x.is_file()})
with (E/'attempt-reserved.json').open('x') as f:json.dump(dict(utc=now(),whole_board_attempt=1,max_global_attempts=1,local_attempts=0),f,indent=2);f.write('\n')
rc=run('final-krt-route',[B/'venv/bin/python3','py_router/route.py',w/'in.kicad_pcb',w/'out.kicad_pcb']+args,cwd=K,timeout=2400)
save(w/'execution.json',dict(utc=now(),whole_board_attempt=1,exit_code=rc,condition_args=args,input_unchanged=digest(w/'in.kicad_pcb')==digest(source/'main.kicad_pcb')))
raise SystemExit(rc)
