from common import *
import ast
start=json.loads((E/'start.json').read_text());gate=json.loads((E/'equivalence-gate.json').read_text());smoke=json.loads((E/'smoke-gate.json').read_text());freeze=json.loads((E/'main-freeze.json').read_text());assessment=json.loads((E/'assessment.json').read_text())
assert gate['pass_equivalence'] and smoke['pass'];assert gate['utc']<smoke['utc']<freeze['utc']
assert smoke['utc']<start['stage0_deadline_utc']
for label,row in gate['inputs'].items():
 for file,key in [('main.kicad_pcb','relaxed_pcb_sha256'),('main.kicad_pro','relaxed_project_sha256'),('corrected.dsn','relaxed_dsn_sha256')]:assert sha(E/'inputs'/label/file)==row[key],(label,file)
for name,h in freeze['scripts'].items():assert sha(E/name)==h,('frozen script changed',name)
assert sha(E/'driver.ts')==freeze['driver_sha256']
for cell,(label,router) in freeze['cells'].items():
 proc=E/'processes'/(label+'-'+router+'-route');rec=json.loads((proc/'record.json').read_text());assert freeze['utc']<=rec['start_utc']<rec['end_utc'];assert rec['exit_code']==0 and not rec['timed_out']
 assert json.loads((E/'runs'/label/router/'execution.json').read_text())['original_input_copy_unchanged']
 independent=json.loads((E/'inspection'/label/router/'independent.json').read_text());assert independent['utc']>rec['end_utc']
 assert (E/'inspection'/label/router/'drc.json').is_file() and (E/'inspection'/label/router/'transfer-diff.json').is_file()
 if independent['measured_unconnected_count']:assert all(x is None for x in independent['metrics'].values())
 assert independent['physical']['In1_signal_tracks']==0
 assert all(k=='0.6/0.3' for k in independent['physical']['via_diameter_drill_mm_counts'])
 assert independent['metrics']==assessment['cells'][cell]['metrics']
for label,router in [('smoke4','fab'),('smoke4','krt'),('smoke4','free'),('smoke2','fab')]:
 rec=json.loads((E/'processes'/(label+'-'+router+'-route')/'record.json').read_text());assert gate['utc']<rec['start_utc']<smoke['utc']
 d=json.loads((E/'inspection'/label/router/'independent.json').read_text());assert all(x==0 for x in d['metrics'].values())
# One exact Main route process per declared cell; launch directories reject reuse.
route_dirs=sorted(p.name for p in (E/'processes').glob('main*-route'));assert route_dirs==['main2-fab-route','main4-fab-route','main4-free-route','main4-krt-route']
# Preserve historical input and evidence source hashes.
prov=json.loads((E/'source-117-provenance.json').read_text())
for name,h in prov['files'].items():assert sha(E/'source-117'/name)==h
for name,h in json.loads((E/'source-115-provenance.json').read_text())['files'].items():assert sha(R/name)==h
# Baseline tracked worktree files must remain unchanged; staging may contain additions only.
git=['git','--git-dir='+GIT,'--work-tree='+str(R)]
assert subprocess.run(git+['diff','--quiet']).returncode==0
changes=subprocess.check_output(git+['diff','--cached','--name-status',start['base_commit']],text=True).splitlines()
for row in changes:
 status,path=row.split('\t');assert status=='A',row
 assert path.startswith('hardware/kicad/qualification/issue-119-promising-tools-relaxed/') or path=='docs/issue-119-promising-tools-relaxed-conditions.md',row
syntax=[]
for p in E.glob('*.py'):ast.parse(p.read_text());syntax.append(p.name)
json_count=0
for p in E.rglob('*.json'):json.loads(p.read_text());json_count+=1
assert not [p for p in E.rglob('*') if p.suffix in ['.jar','.so','.zip','.tar','.gz']]
save(E/'verification.json',dict(utc=utc(),all_checks_pass=True,stage0_before_deadline=True,all_input_hashes_unchanged=True,frozen_scripts_unchanged=True,Main_route_processes=route_dirs,all_independent_inspections_executed=True,all_smoke_four_metrics_zero=True,Main_null_semantics_correct=True,standard_vias_verified_all_cells=True,In1_signal_tracks_zero_all_cells=True,source117_commit=prov['commit'],source117_archive_hashes_match=True,existing_files_unchanged=True,staged_additions_only=changes,python_syntax_checks=syntax,parsed_json_files=json_count,qualification_passes={c:d['pass_acceptance'] for c,d in assessment['cells'].items()}))
print('VERIFIED',utc())
