"""Submission-only hash/AST/link/saved-result checks. No EDA or routing call."""
import ast,datetime,gzip,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[4];EV=ROOT/'evidence'
def raw(p):
    if p.is_file():return p.read_bytes()
    return gzip.decompress(p.with_name(p.name+'.gz').read_bytes())
def sha(p):return hashlib.sha256(raw(p)).hexdigest()
prior=json.loads((EV/'preserved-files.json').read_text())
for name,h in prior.items():assert sha(REPO/name)==h,name
snapshot=json.loads((EV/'recovery-01/preserved-uncommitted.json').read_text())
for name,h in snapshot.items():assert sha(ROOT/name)==h,name
old=json.loads((ROOT.parent/'evidence/reuse-hashes.json').read_text())['files']
for name,h in old.items():assert sha(REPO/name)==h,name
records=list((EV/'processes').glob('*/record.json'));fails=[]
for p in records:
    r=json.loads(p.read_text());assert r['end_utc'] and r['exit_code'] is not None,p
    for k in ['stdout','stderr']:assert sha(p.parent/k)==r[k+'_sha256'],p
    for a in r['artifacts']:
        if a['present']:assert sha(EV/a['saved_path'])==a['sha256'],a
    if r['exit_code']!=0:fails.append(p.parent.name)
assert set(fails)=={'smoke-dsn-parity','small-acceptance'},fails
stop=json.loads((EV/'stop-decision.json').read_text());assert stop['experiment_restart_forbidden']
for p in records:assert json.loads(p.read_text())['start_utc']<stop['utc'],'postSTOP experimental record'
ledger=json.loads((EV/'attempt-ledger.json').read_text());assert len(ledger['small'])==1 and len(ledger['attempts'])==1 and ledger['attempts'][0]['kind']=='initial' and not ledger['initial_all_conditions_pass']
for name in ['smoke','main']:
    parity=json.loads((EV/(name+'-dsn-parity.json')).read_text());assert parity['status']=='PASS_WITH_SCOPE'
    diff=json.loads((EV/'processes'/(name+'-independent-diff')/'diff.json').read_text());assert diff['only_authorized_numeric_token_diff'] and len(diff['semantic_changes'])==1
small=json.loads((EV/'small-acceptance.json').read_text());assert small['status']=='PASS_WITH_SCOPE' and all(small[k]==0 for k in ['required_unconnected','wrong_net_actual_copper_contacts','targeted_material_violations','unexplained_transfer_changes'])
for name in ['smoke','main']:
    r=json.loads((EV/'processes'/(name+'-read-corrected')/'effective.json').read_text());assert all(x['clearance_mm']>=.2 for x in r['clearance_matrix'] if x['class_a']!='null' and x['class_b']!='null')
    assert all(x['clearance_class']!='null' for kind in ['pins','obstacles','traces'] for x in r[kind])
summary=json.loads((EV/'recovery-01/router-terminal-summary.json').read_text());assert summary['last_completed_pass']==512 and summary['declared_max_passes']==100 and summary['router_incomplete_count']==35
assert all(summary[k] is None for k in ['main_required_physical_unconnected','main_wrong_net_actual_copper_contacts','main_target_material_violations','main_postreturn_unexplained_transfer_changes'])
assert not any('main-initial-ses-import' in str(p) or 'main-initial-return-drc' in str(p) for p in records)
for p in ROOT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
links=0
for p in [REPO/'docs/issue-87-native-main-routing.md',REPO/'docs/project-status.md',REPO/'docs/eda-path-history.md',ROOT/'README.md',EV/'recovery-01/README.md']:
    for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        if link.startswith(('https:','http:','#')):continue
        target=link.split('#')[0]
        if target:assert (p.parent/target).exists(),(p,target);links+=1
archives=EV/'exact-archives.json'
if archives.exists():
    for a in json.loads(archives.read_text()):
        assert sha(EV/a['original'])==a['raw_sha256']
        assert hashlib.sha256((EV/a['archive']).read_bytes()).hexdigest()==a['archive_sha256']
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ['submission-integrity.json','effort-ledger.json']}
out=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_epoch_files_unchanged=len(prior),earlier_resume02_files_unchanged=len(old),recovery_saved_files_unchanged=len(snapshot),process_records_verified=len(records),preserved_preparation_failures=fails,no_new_route=True,small_initial_confirmation_counts=[1,1,0],main_physical_metrics_unmeasured=True,link_count=links,python_ast=True,raw_artifact_hashes=True,technical_main_pass=False,manifest_sha256=manifest)
(EV/'submission-integrity.json').write_text(json.dumps(out,indent=2)+'\n');print('Saved-only verification:',len(prior),'prior files,',len(snapshot),'recovery files,',len(records),'processes; small/Main/confirmation1/1/0, Main metrics null')
