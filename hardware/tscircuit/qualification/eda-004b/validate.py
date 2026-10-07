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
def terminal_contract(result, ledger):
 assert result['primary_classification'] == 'ENVIRONMENT_BLOCKED'
 assert result['first_terminal_gate'] == 'P1_CONVERTER_MODULE_LOAD'
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
 terminal_contract(read('final-classification.json'), read('attempt-ledger.json'))
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
 for value in ['EDA-004B','ENVIRONMENT_BLOCKED','P1_CONVERTER_MODULE_LOAD']:
  assert all(value in text for text in [docs,dashboard,report]), value
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
 subprocess.run(['node','--check','task/data/project-status.js'],cwd=ROOT,check=True)
 subprocess.run(['git','diff','--check',BASE],cwd=ROOT,check=True)
 print(json.dumps({'result':'PASS','meaning':'Blocked evidence integrity; no board/geometry qualification','protected_file_count':len(protected),'fixed_input_hashes':len(EXPECTED),'main_attempts':0,'confirmation_attempts':0,'geometry_reconciliation':'NOT ENTERED','raw_smoke_capture':'MISSING / disclosed'}))
