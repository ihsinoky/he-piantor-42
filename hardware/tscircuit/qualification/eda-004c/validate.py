"""Read-only validation of a stopped experiment; never installs/generates/routes."""
import datetime,gzip,hashlib,importlib.util,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[3]
E=ROOT/'evidence'
BASE='ca0c98db53ddd22ca2365246d67589e42fb7c9a5'

def read(name):return json.loads((E/name).read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def terminal(result,ledger,stop):
 assert result['classification']=='CONVERSION_BLOCKED'
 assert result['first_terminal_gate']==stop['first_terminal_gate']=='C1_DUPLICATE_GND_PAD_NET_LOSS'
 assert result['route_counts']=={'initial':0,'fresh_confirmation':0,'main':0}
 assert ledger['attempts']==[] and ledger['initial_all_conditions_pass'] is False and ledger['main_attempts']==0
 assert result['after_stop_experiment_count']==stop['experimental_processes_after_stop']==0
 assert result['technical_qualification_complete'] is False
 assert result['terminal_reporting_complete'] is True
 assert result['backend_adopted'] is False and result['Main_qualified'] is False
 for metric in result['required_acceptance_metrics'].values():
  assert metric=={'initial':None,'confirmation':None,'status':'NOT ENTERED'}
 for stage in ['KiCad_to_DSN','local_headless_Freerouting','SES_to_KiCad','post_route_DRC_independent_island_checks','fresh_confirmation','byte_reproducibility','normalized_connection_shape_reproducibility']:
  assert result['stages'][stage]=='NOT ENTERED'

if __name__=='__main__':
 protected=read('protected-start.json')
 for name,h in protected.items():
  assert digest(REPO/name)==h,'Protected byte change: '+name
  assert hashlib.sha256(subprocess.check_output(['git','show',BASE+':'+name],cwd=REPO)).hexdigest()==h
 assert len(protected)>350
 assert read('protected-end.json')['sha256']==protected and read('protected-end.json')['byte_hash_match'] is True
 prod=json.loads((REPO/'hardware/tscircuit/package.json').read_text())
 assert prod['dependencies']['tscircuit']=='0.0.2646'
 assert json.loads((REPO/'hardware/tscircuit/package-lock.json').read_text())['packages']['node_modules/tscircuit']['version']=='0.0.2646'
 assert digest(ROOT/'frontend-package-lock.json')=='dec21cc020344ce8c8a769bd3ec92d99186546034974bcb702fc68f9dd7a455f'
 assert (ROOT/'converter-package-lock.json').read_bytes()==(ROOT.parent/'eda-004b/converter-package-lock.json').read_bytes()
 env=read('environment.json')
 assert env['bun_archive_sha256']=='4c446af1a01d7b40e1e11baebc352f9b2bfd12887e51b97dd3b59879cee2743a'
 assert env['router_jar_sha256']=='f6f51bb02245e8e717f9359bd260cc9c5c0b1bc0acc8b7cb2cd5b8ffeb5de3c7'
 assert env['kicad_deb_sha256']=='b7e6d33867631dc44385067b703b4c39eadede2037a260790b19495fe17e43f0'
 source=read('source-build-provenance.json')
 assert source['source_commit']=='f3ea106bdc65ca901e9b23255ad3be0bd2a624ab' and source['git_diff']==''
 assert source['dependency_substitution'] is False and source['converter_router_source_patch'] is False
 assert source['kicadts_build_dist_sha256']==source['installed_kicadts_dist_sha256']
 for name,info in read('artifact-manifest.json').items():
  p=ROOT/name
  assert p.stat().st_size==info['bytes'] and digest(p)==info['sha256'], 'Artifact hash: '+name
 for record_path in E.rglob('record.json'):
  # Self-capture finalizes after validator returns; allow only this explicit runner.
  r=json.loads(record_path.read_text())
  if r['end_utc'] is None:
   assert record_path.parent.name.startswith('validation-'), 'Incomplete process '+str(record_path)
   continue
  assert isinstance(r['exit_code'],int) or 'launch_error' in r
  assert datetime.datetime.fromisoformat(r['end_utc'])>=datetime.datetime.fromisoformat(r['start_utc'])
  for stream in ['stdout','stderr']:
   stream_path=record_path.parent/r.get(stream+'_saved_path',stream)
   data=stream_path.read_bytes()
   if r.get(stream+'_encoding')=='gzip':
    assert digest(stream_path)==r[stream+'_compressed_sha256']
    data=gzip.decompress(data)
   assert hashlib.sha256(data).hexdigest()==r[stream+'_sha256']
  evidence_base=record_path.parents[2]
  for a in r['artifacts']:
   if a['present']:assert digest(evidence_base/a['saved_path'])==a['sha256']
  assert r['display_unset'] is True
 result=read('final-classification.json');ledger=read('attempt-ledger.json');stop=read('stop-decision.json')
 terminal(result,ledger,stop)
 experimental_names=['kicadts-','bun-','frontend-','converter-','kicad-','pcbnew-','freerouting-','smoke-','input-reconciliation']
 for p in (E/'processes').glob('*/record.json'):
  r=json.loads(p.read_text())
  if any(p.parent.name.startswith(prefix) for prefix in experimental_names):
   assert datetime.datetime.fromisoformat(r['end_utc'])<=datetime.datetime.fromisoformat(stop['recorded_utc']), 'Experiment after stop'
  command=' '.join(r['command'])
  assert 'ExportSpecctraDSN(' not in command and 'ImportSpecctraSES(' not in command
  if '-jar' in r['command'] and 'freerouting.jar' in command:assert '-help' in r['command'] and '-de' not in r['command'] and '-do' not in r['command']
 contract=read('run-contract.json')
 assert contract['frozen_for_routing'] is False and contract['route_attempt_count']==0
 assert contract['route_command'] is None and contract['maximum_passes'] is None
 assert (E/'run-contract.sha256').read_text().split()[0]==digest(E/'run-contract.json')
 inp=load('input_replay',ROOT/'check-input.py')
 raw=json.loads((E/'processes/smoke-generation-corrected/smoke.circuit.json').read_text())
 assert inp.check(raw)==read('input-reconciliation.json')
 out=load('output_replay',ROOT/'check-boundary.py')
 actual=out.compare(json.loads((E/'processes/kicad-inventory/board-inventory.json').read_text()),json.loads((E/'processes/smoke-conversion/smoke.kicad_pro').read_text()),(E/'processes/smoke-conversion/smoke.kicad_sch').read_text())
 saved=read('boundary-reconciliation.json');saved.pop('recorded_utc')
 # JSON roundtrip converts tuple semantic values to arrays.
 assert json.loads(json.dumps(actual))==saved and actual['status']=='FAIL'
 assert sum(e['kind']=='physical_pad_net' for e in actual['errors'])==1
 drc=json.loads((E/'processes/kicad-pre-route-drc/pre-route-drc.json').read_text())
 assert sum(x['type']=='shorting_items' for x in drc['violations'])==1
 assert len(drc['unconnected_items'])==2
 erc=json.loads((E/'processes/kicad-synthetic-erc/synthetic-erc.json').read_text())
 violations=[v for sheet in erc['sheets'] for v in sheet['violations']]
 assert len(violations)==18 and sum(v['severity']=='error' for v in violations)==2
 faults=read('checker-fault-tests.json')
 assert faults['status']=='PASS' and faults['count']==len(faults['tests'])==26 and all(t['detected'] for t in faults['tests'])
 assert read('control-fault-tests.json')['status']=='PASS'
 failure=read('control-fault-raw/processes/failure/record.json')
 assert failure['exit_code']==7 and not (E/'control-fault-raw/processes/downstream').exists()
 assert read('processes/input-reconciliation/record.json')['exit_code']==1
 assert read('processes/input-reconciliation-corrected/record.json')['exit_code']==0
 assert read('processes/smoke-conversion/record.json')['start_utc']>read('processes/input-reconciliation-corrected/record.json')['end_utc']
 assert not (ROOT.parent/'eda-004b/evidence/raw/smoke.circuit.json.gz').exists()
 effort=read('effort-ledger.json')
 assert effort['issue_ai_hours_estimate']<4 and effort['known_cumulative_ai_hours_estimate']<16
 assert effort['human_active_hours'] is None and effort['measured_engineer_hours'] is None
 report=REPO/'docs/alternate-physical-backend-smoke-requalification.md'
 docs=REPO/'docs/project-status.md';dashboard=REPO/'task/data/project-status.js'
 for p in [report,docs,dashboard,ROOT/'README.md']:
  text=p.read_text()
  assert 'CONVERSION_BLOCKED' in text and 'C1_DUPLICATE_GND_PAD_NET_LOSS' in text and 'EDA-004C' in text
 for p in [report,docs,ROOT/'README.md']:
  for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if target.startswith(('http:','https:','#')):continue
   assert (p.parent/target.split('#')[0]).exists(),str(p)+' missing '+target
 changed=set(subprocess.check_output(['git','diff','--name-only',BASE],cwd=REPO,text=True).splitlines())
 changed.update(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=REPO,text=True).splitlines())
 for p in changed:
  assert p.startswith('hardware/tscircuit/qualification/eda-004c/') or p in ['docs/alternate-physical-backend-smoke-requalification.md','docs/project-status.md','task/data/project-status.js'], 'Scope: '+p
 subprocess.run(['node','--check','task/data/project-status.js'],cwd=REPO,check=True)
 subprocess.run(['git','diff','--check',BASE],cwd=REPO,check=True)
 print(json.dumps({'status':'PASS','protected_files':len(protected),'artifacts':len(read('artifact-manifest.json')),'classification':result['classification'],'meaning':'Evidence integrity/limited checker replay only; conversion remains FAIL, routing NOT ENTERED'}))
