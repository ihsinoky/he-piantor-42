"""Verify provenance, immutable baseline/source, gates, records, and additive scope."""
import datetime,hashlib,json,pathlib,subprocess
E=pathlib.Path(__file__).resolve().parent;ROOT=E.parents[4];T=pathlib.Path('/tmp/issue-105-fab-router');G=['git','--git-dir='+str(T/'git'),'--work-tree='+str(ROOT)]
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads((E/p).read_text())
base=load('baseline-verification.json')['base']
rows=subprocess.check_output(G+['ls-tree','-r',base]).decode().splitlines();errors=[]
for row in rows:
 meta,name=row.split('\t');p=ROOT/name
 if not p.is_file():errors.append(name);continue
 data=p.read_bytes();blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
 if blob!=meta.split()[2]:errors.append(name)
assert not errors,errors
for name,sha in load('source-manifest.json').items():assert h(T/'fab_router'/name)==sha,name
assert not subprocess.check_output(['git','diff','HEAD','--','src','spec'],cwd=T/'fab_router').strip()
for stage in ['smoke','main']:
 rec=load('processes/'+stage+'/record.json');assert rec['exit_code']==0 and not rec['external_timeout']
 for name,item in rec['files'].items():assert h(E/'processes'/stage/name)==item['sha256'],name
 expected_argv=[str(T/'bun/bun-linux-x64/bun'),'run',str(E/'driver.ts'),str(T/'fab_router'),str(E/'processes'/stage/'corrected.dsn'),str(E/'processes'/stage)]
 assert rec['argv']==expected_argv
 result=load('processes/'+stage+'/result.json');settings=result['report']['effectiveSettings']
 assert load('processes/'+stage+'/requested-settings.json')['settings']=={'timeBudgetMs':1800000,'detailedRouter':'tiles'}
 assert settings==load('processes/smoke/result.json')['report']['effectiveSettings']
 assert load(stage+'-ses-inspection.json')['paths_below_020mm']==0
config=load('settings-comparison-before-main.json')
assert config['changed_fields']=={'detailedRouter':{'before':'off','after':'tiles'}}
assert config['recorded_utc']<load('processes/main/record.json')['start_utc']
assert load('main-preflight/effective-settings-before.json')['effectiveSettings']==load('processes/main/result.json')['report']['effectiveSettings']
for stage in ['smoke','main']:
 assert load('processes/'+stage+'/effective-settings-before.json')['effectiveSettings']==load('processes/'+stage+'/result.json')['report']['effectiveSettings']
assert load('smoke-gate.json')['main_allowed'] is True
assert load('smoke-gate.json')['validated_utc']<load('processes/main/record.json')['start_utc']
a=load('assessment.json');assert a['smoke_invocations']==a['main_invocations']==1
if a['main_unrouted_measured']:assert all(v is None for v in a['independent_metrics'].values())
assert a['self_vs_independent']['smoke_agrees']
assert all(a['self_roundtrip_consistency'].values())
assert sum(x['incomplete'] for x in a['report']['perNet'])==a['main_unrouted_measured']
for stage in ['smoke-ses-import','smoke-read-return','smoke-prepare-library','smoke-drc','smoke-independent']:assert load('processes/'+stage+'/record.json')['exit_code']==0
for name,sha in load('oracle-hashes.json').items():assert h(ROOT/name)==sha
paths=[p for p in E.parent.rglob('*') if p.is_file()]
assert not any('node_modules' in p.parts or p.suffix in ['.deb','.zip','.so','.pyc'] for p in paths)
assert all(not p.read_bytes().startswith(b'\x7fELF') for p in paths)
now=datetime.datetime.now(datetime.timezone.utc);deadline=datetime.datetime.fromisoformat(load('timebox.json')['deadline_utc']);assert now<deadline
out=dict(status='PASS',verified_utc=now.isoformat(),base_commit=base,baseline_files_unchanged=len(rows),source_manifest_unchanged=True,router_src_and_spec_git_diff_empty=True,strict_single_configuration=True,smoke_gate_precedes_main=True,process_hashes_match=True,main_null_policy=True,oracle_hashes_match=True,dependency_bodies_excluded=True,within_two_hour_timebox=True)
(E/'verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
