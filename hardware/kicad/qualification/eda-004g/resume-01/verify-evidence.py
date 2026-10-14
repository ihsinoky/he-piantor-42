"""Submission integrity checks only. Does not launch/fix qualification experiments."""
import ast
import gzip
import json
from pathlib import Path
from capture import ROOT,digest,save,utc
old=json.loads((ROOT/'evidence/preserved-inputs.json').read_text())
print(type(old), list(old)[:5] if isinstance(old,dict) else len(old))
checks={}
items=old.get('files',old)
if isinstance(items,list):items={x['path']:x['sha256'] for x in items}
for path,value in items.items():
    if isinstance(value,dict):value=value['sha256']
    target=ROOT.parents[4]/path
    assert digest(target)==value,('prior evidence changed',path)
checks['preserved_old_files']=len(items)
for contract,freeze in [('model-contract-v1.json','model-contract-freeze-v1.json'),('main-contract-v1.json','main-contract-freeze-v1.json')]:
    record=json.loads((ROOT/'evidence'/freeze).read_text());assert record['sha256']==digest(ROOT/contract)
checks['both_frozen_contracts_unchanged']=True
for r in (ROOT/'evidence/processes').glob('*/record.json'):
    record=json.loads(r.read_text());folder=r.parent
    assert digest(folder/'stdout')==record['stdout_sha256'] and digest(folder/'stderr')==record['stderr_sha256']
    for a in record['artifacts']:
        if a['present']:
            target=ROOT/'evidence'/a['saved_path']
            if target.exists():assert digest(target)==a['sha256']
            else:
                import hashlib
                assert hashlib.sha256(gzip.decompress(target.with_suffix(target.suffix+'.gz').read_bytes())).hexdigest()==a['sha256']
checks['raw_process_records']=len(list((ROOT/'evidence/processes').glob('*/record.json')))
for a in json.loads((ROOT/'evidence/library-evidence-archives.json').read_text()):
    path=ROOT/'library'/a['archive'];assert digest(path)==a['archive_sha256']
    import hashlib
    assert hashlib.sha256(gzip.decompress(path.read_bytes())).hexdigest()==a['expanded_sha256']
checks['library_archives_exact']=True
for p in ROOT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
checks['python_ast_syntax']=True
assert json.loads((ROOT/'evidence/attempt-ledger.json').read_text())['attempts']==[]
assert json.loads((ROOT/'evidence/stop-decision.json').read_text())['experiment_restart_forbidden']
checks['main_and_confirmation_routes_zero']=True
save(ROOT/'evidence/submission-integrity.json',dict(utc=utc(),checks=checks,technical_main_pass=False,required_fault_injections='NOT_ENTERED',scope='Evidence preservation/syntax only, not checker qualification'))
print(checks)
