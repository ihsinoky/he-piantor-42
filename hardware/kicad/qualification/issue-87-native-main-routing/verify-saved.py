"""Submission-only saved evidence verification; no EDA process or acceptance rerun."""
import ast,gzip,hashlib,json,re
from pathlib import Path
from prepare import ROOT,REPO,digest,save,utc
def raw_digest(p):
    return digest(p) if p.exists() else hashlib.sha256(gzip.decompress(p.with_name(p.name+'.gz').read_bytes())).hexdigest()
f=json.loads((ROOT/'evidence/reuse-hashes.json').read_text())
for path,h in f['files'].items():assert digest(REPO/path)==h,path
records=list((ROOT/'evidence/processes').glob('*/record.json'))
failures=[]
for path in records:
    r=json.loads(path.read_text())
    for name in ['stdout','stderr']:assert raw_digest(path.parent/name)==r[name+'_sha256'],path
    assert r['end_utc'] and r['elapsed_seconds']>=0
    for a in r['artifacts']:
        if a['present']:assert digest(ROOT/'evidence'/a['saved_path'])==a['sha256']
    if r['exit_code']!=0:failures.append(dict(process=path.parent.name,exit_code=r['exit_code']))
assert {x['process'] for x in failures}=={'venv','smoke-create','router-source-RoutingJobScheduler'}
a=json.loads((ROOT/'evidence/attempt-ledger.json').read_text());assert a['initial']==a['confirmation']==a['small_roundtrip']==0 and a['dsn_exports']==2
assert json.loads((ROOT/'evidence/stop-decision.json').read_text())['experiment_restart_forbidden']
# Prevent an unrecorded post-STOP experimental process.
stop=json.loads((ROOT/'evidence/stop-decision.json').read_text())['utc']
for path in records:
    r=json.loads(path.read_text());assert r['start_utc']<stop,path
v=json.loads((ROOT/'evidence/via-checker-acceptance.json').read_text());assert v['main_baseline_regression_equal'] and v['status']=='PASS_WITH_SCOPE'
erc=json.loads((ROOT/'evidence/processes/baseline-erc/erc.json').read_text());assert not any(s['violations'] for s in erc['sheets'])
drc=json.loads((ROOT/'evidence/processes/baseline-drc/drc.json').read_text());assert len(drc['violations'])==61 and len(drc['unconnected_items'])==127
for p in ROOT.glob('*.py'):ast.parse(p.read_text())
links=0
for p in [ROOT/'README.md',REPO/'docs/issue-87-native-main-routing.md',REPO/'docs/project-status.md',REPO/'docs/eda-path-history.md',REPO/'docs/native-main-routing-qualification.md']:
    for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        if target.startswith(('http:','https:','#')):continue
        target=target.split('#')[0]
        if target:assert (p.parent/target).exists(),(p,target);links+=1
for a in json.loads((ROOT/'evidence/exact-archives.json').read_text()):
    assert digest(ROOT/'evidence'/a['archive'])==a['archive_sha256']
    assert raw_digest(ROOT/'evidence'/a['original'])==a['sha256']
manifest={str(p.relative_to(ROOT)):digest(p) for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ['submission-integrity.json','effort-ledger.json']}
save(ROOT/'evidence/submission-integrity.json',dict(utc=utc(),old_files_unchanged=len(f['files']),process_records=len(records),raw_hashes_verified=True,known_preparation_failures=failures,no_post_stop_experimental_process=True,local_links=links,python_ast=True,manifest_sha256=manifest,technical_main_pass=False))
print('saved evidence only: old files',len(f['files']),'processes',len(records),'links',links,'Main 0/0/0, no PASS')
