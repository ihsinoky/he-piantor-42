"""Verify supplied cell order, saved evidence and protected pre-existing bytes."""
from common import *
import sys,ast,subprocess
P=E.parent/'issue-131-wing-condition-search/evidence'
protected=json.loads((T/'protected-start.json').read_text());changed={}
for path,h in protected.items():
 p=R/path
 if not p.exists() or digest(p)!=h:changed[path]=None if not p.exists() else digest(p)
assert not changed,changed
cells=['KRT-16-2L-P0300','KRT-17-2L-P0300'];evidence=[]
for cell in cells:
 source=E/'cell-inputs'/cell;raw=E/'runs'/cell;check=E/'inspection'/cell
 condition=json.loads((source/'condition.json').read_text());board=condition['board']
 frozen=json.loads((source/'hashes.json').read_text())
 assert all(digest(source/name)==h for name,h in frozen.items())
 assert digest(source/'main.kicad_pcb')==digest(P/'inputs'/board/'main.kicad_pcb')
 assert digest(raw/'in.kicad_pcb')==digest(source/'main.kicad_pcb')
 assert digest(raw/'in.kicad_pro')==digest(source/'main.kicad_pro')
 assert json.loads((raw/'execution.json').read_text())['exit_code']==0
 a=json.loads((check/'assessment.json').read_text());assert a['pass_acceptance'] and set(a['metrics'].values())=={0}
 pro=json.loads((raw/'out.kicad_pro').read_text());metadata=pro.pop('kicad_routing_tools')
 assert pro==json.loads((source/'main.kicad_pro').read_text())
 assert metadata['power_widths']=={'GND':.3,'HALL_5V':.3}
 width=json.loads((check/'width-audit.json').read_text());assert not width['unexplained_project_changes'] and width['incorrect_vias']==0
 assert all(q['below_required']==0 for q in width['classes'].values())
 readback=json.loads((raw/'effective.json').read_text());c=readback['grid_route_config'];cli=readback['cli_namespace']
 assert c['track_width']==.1 and c['clearance']==.1 and sorted(c['power_net_widths'].values())==[.3,.3]
 assert c['via_size']==.6 and c['via_drill']==.3
 assert cli['escalation']=='off'
 record=json.loads((E/'processes'/(cell+'-route')/'record.json').read_text())
 assert not record['timed_out'] and record['exit_code']==0
 evidence.append(dict(cell=cell,metrics=a['metrics'],width_classes=width['classes'],route_record=record,output_pcb_sha256=digest(raw/'out.kicad_pcb')))
# One route per pitch, and 17 starts only after independent 16 pass.
records=list((E/'processes').glob('*-route/record.json'));assert len(records)==2
assert datetime.datetime.fromisoformat(evidence[1]['route_record']['start_utc'])>datetime.datetime.fromisoformat(json.loads((E/'inspection'/cells[0]/'assessment.json').read_text())['supplemental_audit_utc'])
dc=json.loads((E/'dc-drop-estimate.json').read_text());assert dc['model_function_unchanged'] and len(dc['results'])==32 and len(dc['baseline_reproduction'])==10
for row in dc['results']:
 assert len(row['sensors'])==21
 assert max(row['supply']['kcl_residual_A'],row['ground']['kcl_residual_A'])<1e-7
 assert row['supply']['load_A']>.105 and row['ground']['load_A']>.105
syntax={}
for p in E.rglob('*.py'):ast.parse(p.read_text());syntax[str(p.relative_to(E))]='pass'
for p in E.rglob('*.json'):json.loads(p.read_text())
# Snapshot the protected file hashes in evidence for reproducibility.
import gzip
(E/'protected-start-hashes.json.gz').write_bytes(gzip.compress(json.dumps(protected,sort_keys=True).encode(),mtime=0))
start=json.loads((E/'start.json').read_text());elapsed=(datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(start['start_utc'])).total_seconds()
assert elapsed<3*3600
save(E/'verification.json',dict(utc=now(),elapsed_seconds=elapsed,protected_file_count=len(protected),protected_changes=changed,existing_git_metadata_and_untracked_137_138_included=True,cells=evidence,single_run_per_cell=True,ordered_16_then_17=True,P0200_not_entered='0.30mm 16mm passed',baseline_reproduction_cases=10,dc_cases=32,python_syntax=syntax,json_parse='pass',ci_scope='Only docs and hardware/kicad/qualification additions; engineering-ci heavy jobs and tscircuit-native-spike path filters not applicable; remote CI unknown until publication'))
print('Verification passed',len(protected),'protected files;',elapsed,'seconds')
