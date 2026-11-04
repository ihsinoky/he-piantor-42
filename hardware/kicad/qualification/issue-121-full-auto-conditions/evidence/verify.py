from common import *
import ast
from datetime import datetime
freeze=json.loads((E/'script-freeze.json').read_text())
for f,h in freeze['files'].items():assert sha(E/f)==h,f
assert sha(E/'conditions.json')==freeze['conditions_sha256']
assert sha(E/'equivalence-gate.json')==freeze['gate_sha256']
gate=json.loads((E/'equivalence-gate.json').read_text())
for label,row in gate['inputs'].items():
 for f,h in row['hashes'].items():assert sha(E/'inputs'/label/f)==h
records={p.parent.name:json.loads(p.read_text()) for p in (E/'processes').glob('*/record.json')}
routes={k:v for k,v in records.items() if k.endswith('-krt-route')}
assert set(routes)=={'smoke-cell1-krt-route','main-cell1-krt-route'}
for k,v in records.items():assert v['exit_code']==0 and not v['timed_out'],k
smoke=json.loads((E/'smoke-gates/cell1.json').read_text());ind=json.loads((E/'inspection/main-cell1/krt/independent.json').read_text())
assert smoke['pass'] and ind['pass_acceptance'] and all(v==0 for v in ind['metrics'].values())
assert gate['utc']<routes['smoke-cell1-krt-route']['start_utc']<smoke['utc']<routes['main-cell1-krt-route']['start_utc']<ind['utc']
assert json.loads((E/'stage0.json').read_text())['utc']<json.loads((E/'start.json').read_text())['stage0_deadline_utc']
assert ind['width_pass'] and ind['via_pass'] and ind['plane_role_pass']
assert json.loads((E/'stop.json').read_text())['not_run']==['cell2','cell3','cell4']
for stage in ['smoke','main']:
 label=stage+'-cell1';assert json.loads((E/'runs'/label/'krt/execution.json').read_text())['original_input_copy_unchanged']
 for f in ['drc.json','snapshot.json','transfer-diff.json','physical-readback.json','main.kicad_pcb','main.kicad_pro']:assert (E/'inspection'/label/'krt'/f).is_file()
assert subprocess.check_output(['git','--git-dir='+GIT,'diff','HEAD','--name-only'],text=True)=='' # current additions remain untracked until verification completes
for p in E.rglob('*.json'):json.loads(p.read_text())
for p in E.glob('*.py'):ast.parse(p.read_text())
whitespace=[]
for p in list(E.glob('*.py'))+[R/'docs/issue-121-full-auto-conditions.md']:
 for n,line in enumerate(p.read_text().splitlines(),1):
  if line.rstrip()!=line:whitespace.append([str(p),n])
assert not whitespace
save(E/'verification.json',dict(utc=utc(),pass_verification=True,all_frozen_scripts_unchanged=True,all_prepared_inputs_unchanged=True,gate_before_smoke_before_main=True,stage0_within_45_minutes=True,executed_main_cells=['cell1'],main_reruns=0,smoke_reruns=0,remaining_cells_not_run=True,independent_metrics=ind['metrics'],all_processes_exit_zero_no_timeout=True,all_raw_DRC_saved=True,tracked_file_changes_before_adding=[],authored_python_AST_and_JSON_valid=True,authored_whitespace_errors=whitespace))
print('VERIFICATION PASS',utc())
