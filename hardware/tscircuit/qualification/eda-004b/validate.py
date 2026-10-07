#!/usr/bin/env python3
"""Read-only evidence validation. Does not install, generate or route.
This validates a blocked execution record, not Circuit JSON/KiCad geometry.
"""
import gzip
import hashlib
import json
import re
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
QUAL = Path(__file__).resolve().parent
E = QUAL / 'evidence'
BASE = '20b25914cc7515ab8ba191f5fdcbba6217a37d23'
REVIEW_HEAD = '137f2e5e5cf267177899b06ca824f2daa29153dc'
FIRST_GATE = 'P1_SMOKE_CAPTURE_GUARD_ERROR'
SECONDARY_GATE = 'P1_CONVERTER_MODULE_LOAD'
RECORD_EDITS = {
 'docs/alternate-physical-backend-main-qualification.md',
 'docs/project-status.md', 'task/data/project-status.js',
 *('hardware/tscircuit/qualification/eda-004b/' + name for name in [
  'README.md', 'validate.py', 'test-evidence.py',
  'evidence/attempt-ledger.json', 'evidence/final-classification.json',
  'evidence/converter-package-failure.json', 'evidence/effort-ledger.json',
  'evidence/run-contract.json', 'evidence/run-contract.sha256',
  'evidence/artifact-manifest.json', 'evidence/validation.json',
  'evidence/review-correction.json',
 ]),
}
DESIGN = 'b84585ecc2cf32000285bbf389d9fea255436980'
EXPECTED = {
 'src/qualification/revm1-routing-proof.tsx': '0caa8e53eed298c3cf65715a15a1d671d91de715d4eb8f790eeb13e17a777008',
 'src/qualification/JstGh14.tsx': 'ad23f75d53a917f8f43485b7fe887ff096ab0bdda244e3dc6e44fd73d93c787c',
 'src/qualification/native-support-footprints.tsx': '7b0efff9f5178b589c2ef7085625549bc4701ee24d2841ee7b46785921db55fe',
 'src/components/HallKey.tsx': '0241daa3e2640bc870537ba3fa6571868858345f361456d80f73849dad32495c',
 'qualification/eda-003c/latest-stock/package-lock.json': 'dec21cc020344ce8c8a769bd3ec92d99186546034974bcb702fc68f9dd7a455f',
}
def digest(data):
 return hashlib.sha256(data).hexdigest()
def read(name):
 return json.loads((E/name).read_text())
def terminal_contract(result, ledger, secondary):
 assert result['primary_classification'] == 'ENVIRONMENT_BLOCKED'
 for record in [result, ledger, secondary]:
  assert record['first_terminal_gate'] == FIRST_GATE
  assert record['sequence_deviation'] is True
 for record in [result, ledger]:
  assert record['failure_origin'] == 'EXECUTOR_VALIDATION_CAPTURE'
  assert record['terminal_reporting_complete'] is True
  assert record['technical_qualification_complete'] is False
  assert 'qualification_execution_complete' not in record
  assert record['immediate_stop_compliance'] is False
  observations = record['ordered_failure_observations']
  assert [o['sequence'] for o in observations] == [1, 2]
  assert [o['gate'] for o in observations] == [FIRST_GATE, SECONDARY_GATE]
  assert [o['origin'] for o in observations] == ['EXECUTOR_VALIDATION_CAPTURE', 'SECONDARY_ENVIRONMENT_OBSTACLE']
  assert [o['evidence_log'] for o in observations] == ['smoke-generation.log', 'smoke-conversion.log']
  assert all(o['exit_code'] is None and o['observed_at_utc'] is None for o in observations)
 assert result['ordered_failure_observations'] == ledger['ordered_failure_observations']
 assert result['secondary_environment_gate'] == SECONDARY_GATE
 assert secondary['observed_gate'] == SECONDARY_GATE
 assert secondary['observation_role'] == 'SECONDARY_ENVIRONMENT_OBSTACLE'
 assert secondary['failure_sequence'] == 2
 assert secondary['operation_after_first_failure'] is True
 assert ledger['operations_after_first_failure'] == [{
  'operation': 'converter module load', 'count': 1, 'observed_gate': SECONDARY_GATE,
  'sequence_deviation': True, 'exit_code': None,
 }]
 assert result['main_qualified'] is False
 for name in ['required_unrouted','wrong_net_copper_components','targeted_material_violations','unexplained_conversion_loss']:
  assert result['main_metrics'][name] is None, name
 assert result['erc_status'] == 'NOT ENTERED'
 assert result['drc_status'] == 'NOT ENTERED'
 assert result['independent_kicad_reconciliation'] == 'NOT ENTERED'
 assert result['geometry_fault_injection'] == 'NOT ENTERED'
 assert result['stages']['2'] == result['stages']['3'] == result['stages']['4'] == 'NOT ENTERED'
 for name in ['smoke','main_initial','main_confirmation']:
  assert ledger[name] == []
 for name in ['smoke_routing_process_count','main_initial_count','main_confirmation_count']:
  assert ledger[name] == 0
 assert ledger['frontend_smoke_generation_processes'] == 1
 assert result['evidence_completeness'] == 'PARTIAL'
 assert result['missing_raw_smoke_json'] is True
 assert result['main_initial_count'] == result['main_confirmation_count'] == result['smoke_router_count'] == 0

if __name__ == '__main__':
 protected = read('protected-files.json')['sha256']
 for path, expected in protected.items():
  assert digest((ROOT/path).read_bytes()) == expected, f'Protected file changed: {path}'
  assert digest(subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=ROOT)) == expected
 for path, expected in EXPECTED.items():
  full = 'hardware/tscircuit/' + path
  assert digest(subprocess.check_output(['git','show',f'{DESIGN}:{full}'],cwd=ROOT)) == expected
  assert digest((ROOT/full).read_bytes()) == expected
 production = json.loads((ROOT/'hardware/tscircuit/package.json').read_text())
 assert production['dependencies']['tscircuit'] == '0.0.2646'
 lock = json.loads((ROOT/'hardware/tscircuit/package-lock.json').read_text())
 assert lock['packages']['node_modules/tscircuit']['version'] == '0.0.2646'
 for p in E.rglob('*.json'):
  json.loads(p.read_text())
 for path, info in read('artifact-manifest.json').items():
  p = ROOT/path
  assert p.stat().st_size == info['bytes']
  assert digest(p.read_bytes()) == info['sha256'], f'Evidence changed: {path}'
 for path, info in read('raw-manifest.json').items():
  data = (E/'raw'/path).read_bytes()
  assert digest(data) == info['compressed_sha256']
  unpacked = gzip.decompress(data)
  assert len(unpacked) == info['uncompressed_bytes']
  assert digest(unpacked) == info['uncompressed_sha256']
 contract = read('run-contract.json')
 assert contract['frozen_for_routing'] is False and contract['command_execution_count'] == 0
 assert (E/'run-contract.sha256').read_text().split()[0] == digest((E/'run-contract.json').read_bytes())
 terminal_contract(read('final-classification.json'), read('attempt-ledger.json'), read('converter-package-failure.json'))
 effort = read('effort-ledger.json')
 assert effort['checkpoints']['P1']['gate'] == FIRST_GATE
 assert effort['experimentation_after_terminal_gate'] is True
 assert effort['immediate_stop_compliance'] is False
 assert effort['first_failure_observed_at_utc'] is None
 failure = read('converter-package-failure.json')
 assert failure['error_code'] == 'ERR_MODULE_NOT_FOUND'
 assert failure['dist_exists'] is False
 assert set(failure['installed_files']) == {'LICENSE','README.md','package.json'}
 assert 'kicadts/dist/index.js' in (E/'smoke-conversion.log').read_text()
 assert 'routingDisabled retained copper; STOP' in (E/'smoke-generation.log').read_text()
 assert not (E/'raw/smoke.circuit.json.gz').exists()
 accepted = ROOT/'hardware/tscircuit/qualification/eda-003c/evidence/raw/latest-main.circuit.json.gz'
 assert digest(gzip.decompress(accepted.read_bytes())) == '97d51d510ecc7096261ad36297b48939609a14435a24926967b61197ed951131'
 docs = (ROOT/'docs/project-status.md').read_text()
 dashboard = (ROOT/'task/data/project-status.js').read_text()
 report = (ROOT/'docs/alternate-physical-backend-main-qualification.md').read_text()
 for value in ['EDA-004B','ENVIRONMENT_BLOCKED',FIRST_GATE,SECONDARY_GATE]:
  assert all(value in text for text in [docs,dashboard,report,(QUAL/'README.md').read_text()]), value
 for text in [docs, dashboard, report, (QUAL/'README.md').read_text()]:
  assert not re.search(r'ENVIRONMENT_BLOCKED\s*(?:—|/)\s*' + SECONDARY_GATE, text), 'Secondary failure promoted to primary prose gate'
 correction = read('review-correction.json')
 assert correction['reviewed_head'] == REVIEW_HEAD
 assert correction['first_terminal_gate'] == FIRST_GATE
 assert correction['secondary_environment_gate'] == SECONDARY_GATE
 assert correction['first_failure_origin'] == 'EXECUTOR_VALIDATION_CAPTURE'
 assert correction['sequence_deviation'] is True and correction['immediate_stop_compliance'] is False
 assert correction['terminal_reporting_complete'] is True and correction['technical_qualification_complete'] is False
 assert correction['new_experimental_processes'] == 0
 for document in [ROOT/'docs/alternate-physical-backend-main-qualification.md', ROOT/'docs/project-status.md', QUAL/'README.md']:
  for target in re.findall(r'\]\(([^)]+)\)', document.read_text()):
   if target.startswith(('https:', 'http:', '#')):
    continue
   assert (document.parent / target.split('#')[0]).exists(), f'Missing reference: {document}: {target}'
 changed = set(subprocess.check_output(['git','diff','--name-only',BASE],cwd=ROOT,text=True).splitlines())
 changed.update(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines())
 for path in changed:
  assert path.startswith('hardware/tscircuit/qualification/eda-004b/') or path in {
   'docs/alternate-physical-backend-main-qualification.md', 'docs/project-status.md', 'task/data/project-status.js'
  }, f'Out-of-scope change: {path}'
 review_changed = set(subprocess.check_output(['git','diff','--name-only',REVIEW_HEAD],cwd=ROOT,text=True).splitlines())
 review_changed.update(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines())
 assert review_changed <= RECORD_EDITS, f'Non-record edit in review correction: {review_changed - RECORD_EDITS}'
 review_files = subprocess.check_output(['git','ls-tree','-r','--name-only',REVIEW_HEAD,'--','hardware/tscircuit/qualification/eda-004b'],cwd=ROOT,text=True).splitlines()
 preserved = [path for path in review_files if path not in RECORD_EDITS]
 for path in preserved:
  assert (ROOT/path).read_bytes() == subprocess.check_output(['git','show',f'{REVIEW_HEAD}:{path}'],cwd=ROOT), f'Review evidence changed: {path}'
 old_contract = json.loads(subprocess.check_output(['git','show',f'{REVIEW_HEAD}:hardware/tscircuit/qualification/eda-004b/evidence/run-contract.json'],cwd=ROOT))
 assert {k:v for k,v in contract.items() if k != 'reason'} == {k:v for k,v in old_contract.items() if k != 'reason'}
 subprocess.run(['node','--check','task/data/project-status.js'],cwd=ROOT,check=True)
 subprocess.run(['git','diff','--check',BASE],cwd=ROOT,check=True)
 subprocess.run(['git','diff','--check',REVIEW_HEAD],cwd=ROOT,check=True)
 print(json.dumps({'result':'PASS','meaning':'Reporting chronology/integrity only; no board/geometry/backend qualification','first_terminal_gate':FIRST_GATE,'secondary_environment_gate':SECONDARY_GATE,'immediate_stop_compliance':False,'terminal_reporting_complete':True,'technical_qualification_complete':False,'protected_file_count':len(protected),'review_evidence_preserved_file_count':len(preserved),'fixed_input_hashes':len(EXPECTED),'main_attempts':0,'confirmation_attempts':0,'smoke_routing':0,'geometry_reconciliation':'NOT ENTERED','raw_smoke_capture':'MISSING / disclosed'}))
