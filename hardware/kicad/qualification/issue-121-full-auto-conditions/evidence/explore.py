from common import *
conditions=json.loads((E/'conditions.json').read_text());results={}
save(E/'script-freeze.json',dict(utc=utc(),files={p.name:sha(p) for p in E.glob('*.py')},conditions_sha256=sha(E/'conditions.json'),gate_sha256=sha(E/'equivalence-gate.json')))
for cell,c in conditions.items():
 for stage in ['smoke','main']:
  label=stage+'-'+cell;cfg=E/'configuration'/(label+'.json')
  assert run(label+'-configuration',[R/'.issue113-runtime/venv/bin/python3',E/'read-effective.py',cfg,label,'explicit'])==0
  resolved=json.loads(cfg.read_text());g=resolved['grid_route_config']
  assert g['track_width']==g['clearance']==c['width'] and g['via_size']==c['via'] and g['via_drill']==c['drill']
  assert g['layer_costs']==[1,-1,1,1] and resolved['escalation_policy'][0]==c['escalation']
  assert run(label+'-launcher',['/usr/bin/python3',E/'run-cell.py',label],timeout=1860)==0
  assert run(label+'-inspection',['/usr/bin/python3',E/'independent-check.py',label,'krt'],timeout=180)==0
  result=json.loads((E/'inspection'/label/'krt/independent.json').read_text())
  if stage=='smoke':
   save(E/'smoke-gates'/(cell+'.json'),dict(utc=utc(),**{'pass':result['pass_acceptance']},inspection=result))
   assert result['pass_acceptance']
   if cell=='cell1':save(E/'stage0.json',dict(utc=utc(),**{'pass':True},input_gate_sha256=sha(E/'equivalence-gate.json'),first_smoke_gate_sha256=sha(E/'smoke-gates/cell1.json')))
  else:results[cell]=result;save(E/'results.json',dict(utc=utc(),cells=results))
 if result['pass_acceptance']:
  save(E/'stop.json',dict(utc=utc(),reason='Independent four metrics all zero; remaining cells not run',completed_cell=cell,not_run=[k for k in conditions if k not in results]));break
else:save(E/'stop.json',dict(utc=utc(),reason='All four declared cells exhausted without independent acceptance',completed_cell=None))
print('EXPLORATION FINISHED',utc())
