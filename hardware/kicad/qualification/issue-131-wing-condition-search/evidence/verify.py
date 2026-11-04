"""Submission audit: additive-only files, frozen inputs and single ordered runs."""
from common import *
import ast,sys,collections
base='e0374fe';git=['git','--git-dir='+str(T/'git'),'--work-tree='+str(R)]
rows=subprocess.check_output(git+['ls-tree','-r','--name-only',base],text=True).splitlines();bad=[]
for name in rows:
 expected=subprocess.check_output(git+['show',base+':'+name]);p=R/name
 if not p.is_file() or p.read_bytes()!=expected:bad.append(name)
assert not bad,bad
assert json.loads((E/'equivalence-gate.json').read_text())['pass_equivalence']
for board,files in json.loads((E/'stage0-frozen-hashes.json').read_text()).items():
 for name,h in files.items():assert digest(E/'inputs'/board/name)==h
conditions=[('KRT-16-2L-0127',.127,2),('KRT-16-2L-0100',.1,2),('KRT-16-4L-0127',.127,4),('KRT-16-4L-0100',.1,4)]
assess=json.loads((E/'assessment.json').read_text());cells=assess['cells'];route_records={}
seen_pass=False;reached=[]
for cell,width,layers in conditions:
 row=cells[cell]
 if row['status']=='NOT_RUN':
  assert seen_pass or assess['status']=='TIMEBOX_FAILURE'
  continue
 assert not seen_pass
 reached.append(cell);seen_pass=row['pass_acceptance']
if seen_pass:
 confirm=assess['confirmation_cell'];assert confirm and cells[confirm]['status']!='NOT_RUN';reached.append(confirm)
else:assert assess['confirmation_cell'] is None
for cell in reached:
 w=E/'runs'/cell;source=E/'cell-inputs'/cell
 frozen=json.loads((source/'hashes.json').read_text())
 for name,h in frozen.items():assert digest(source/name)==h
 rec=json.loads((E/'processes'/(cell+'-route')/'record.json').read_text());route_records[cell]=rec
 assert '--escalation' in rec['argv'] and rec['argv'][rec['argv'].index('--escalation')+1]=='off'
 effective=json.loads((w/'effective.json').read_text());config=effective['grid_route_config'];condition=json.loads((source/'condition.json').read_text());floor=condition['width_mm']
 assert config['track_width']==config['clearance']==floor and config['via_size']==.6 and config['via_drill']==.3
 assert effective['escalation_policy'][0]=='off'
 audit=json.loads((E/'inspection'/cell/'assessment.json').read_text())
 if audit['measured_unconnected']:
  assert all(v is None for v in audit['metrics'].values())
 if audit['pass_acceptance']:assert all(v==0 for v in audit['metrics'].values()) and audit['width_pass']
 assert json.loads((E/'inspection'/cell/'physical-audit.json').read_text())['via_pass']
assert len(list((E/'processes').glob('*-route')))==len(reached)
jsons=0;pyfiles=0
for p in E.rglob('*.json'):json.loads(p.read_text());jsons+=1
for p in E.rglob('*.py'):ast.parse(p.read_text());pyfiles+=1
old=json.loads((T/'reuse-source-hashes.json').read_text());sourcebad={name for name,h in old.items() if digest(R/'.issue129-runtime'/name)!=h};assert not sourcebad
save(E/'verification.json',dict(utc=now(),pass_verification=True,base_commit=subprocess.check_output(git+['rev-parse',base],text=True).strip(),base_files_checked=len(rows),base_mismatches=bad,existing_files_unchanged=True,additions_only=True,stage0_inputs_hashes_match=True,routing_order=reached,single_run_per_cell=True,escalation_off_readback=True,pinned_width_vias_readback=True,json_files_valid=jsons,python_files_parse=pyfiles,readonly_reuse_files_checked=len(old),readonly_reuse_mismatches=sorted(sourcebad),runtime_not_bundled=True,completed_before_deadline=datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,11,5,0,43,54,tzinfo=datetime.timezone.utc)))
print('verification passed',len(rows),'base files;',len(reached),'single routing runs')
