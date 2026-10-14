"""Submission integrity only; no qualification rerun, repair or acceptance change."""
import ast,gzip,hashlib,json,re
from pathlib import Path
from capture import ROOT,digest,save,utc
def actual_hash(path):
    if path.exists():return digest(path)
    return hashlib.sha256(gzip.decompress(path.with_suffix(path.suffix+'.gz').read_bytes())).hexdigest()
old=json.loads((ROOT/'evidence/preserved-inputs.json').read_text())
for path,sha in old.items():assert digest(ROOT.parents[4]/path)==sha,path
freeze=json.loads((ROOT/'evidence/contracts-freeze.json').read_text())
assert digest(ROOT/'main-contract-v2.json')==freeze['main'] and digest(ROOT/'model-contract-v2.json')==freeze['models']
for name,sha in freeze['libraries'].items():assert actual_hash(ROOT/'library'/name)==sha
assert digest(ROOT/'auxiliary-contract-v2.json')==json.loads((ROOT/'evidence/auxiliary-contract-freeze.json').read_text())['sha256']
records=list((ROOT/'evidence/processes').glob('*/record.json'))
for path in records:
    record=json.loads(path.read_text())
    for name in ['stdout','stderr']:assert actual_hash(path.parent/name)==record[name+'_sha256']
    for a in record['artifacts']:
        if a['present']:assert actual_hash(ROOT/'evidence'/a['saved_path'])==a['sha256']
for a in json.loads((ROOT/'evidence/exact-archives.json').read_text()):
    assert digest(ROOT/a['archive'])==a['archive_sha256'] and actual_hash(ROOT/a['original'])==a['original_sha256']
for path in ROOT.glob('*.py'):ast.parse(path.read_text(),filename=str(path))
assert json.loads((ROOT/'evidence/stop-decision.json').read_text())['experiment_restart_forbidden']
assert not json.loads((ROOT/'evidence/attempt-ledger.json').read_text())['attempts']
links=0
for path in [ROOT/'README.md',ROOT.parents[4]/'docs/native-main-routing-qualification.md',ROOT.parents[4]/'docs/project-status.md',ROOT.parents[4]/'docs/eda-path-history.md']:
    for link in re.findall(r'\]\(([^)]+)\)',path.read_text()):
        if link.startswith(('http:','https:','#')):continue
        target=link.split('#')[0]
        if target:assert (path.parent/target).exists(),(path,target);links+=1
erc=json.loads((ROOT/'evidence/processes/initial-erc/erc.json').read_text());assert not any(s['violations'] for s in erc['sheets'])
drc=json.loads((ROOT/'evidence/processes/initial-pre-route-drc/drc.json').read_text());assert len(drc['violations'])==61 and len(drc['unconnected_items'])==127
faults=json.loads((ROOT/'evidence/checker-fault-acceptance.json').read_text());assert len(faults['cases'])==4 and all(x['detected'] for x in faults['cases'].values())
save(ROOT/'evidence/submission-integrity.json',dict(utc=utc(),prior_files_unchanged=len(old),all_three_frozen_oracles_unchanged=True,process_records_checked=len(records),raw_artifact_hashes=True,exact_archives=True,python_ast=True,local_links_checked=links,recorded_four_synthetic_fault_detections=True,recorded_erc_violations=0,recorded_printing_drc_violations=61,main_routes=0,main_technical_pass=False,scope='Submission integrity, not new qualification experiment or geometry/constraint repair.'))
print('old files',len(old),'processes',len(records),'links',links,'frozen/raw/archive/AST/counts verified; no Main PASS')
