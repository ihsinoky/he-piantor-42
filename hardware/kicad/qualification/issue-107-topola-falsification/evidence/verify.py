"""Verify evidence consistency and preserve every pre-existing tracked file."""
import ast,datetime,hashlib,json,pathlib,subprocess
E=pathlib.Path(__file__).resolve().parent;ROOT=E.parents[4];G=['git','--git-dir=/tmp/issue-107-topola/git','--work-tree='+str(ROOT)]
base=json.loads((E/'baseline-verification.json').read_text())['base']
rows=subprocess.check_output(G+['ls-tree','-r',base],text=True).splitlines()
for row in rows:
 meta,name=row.split('\t');assert subprocess.check_output(G+['hash-object',str(ROOT/name)],text=True).strip()==meta.split()[2],name
s=json.loads((E/'processes/smoke/record.json').read_text());a=json.loads((E/'assessment.json').read_text());w=json.loads((E/'smoke-ses-inspection.json').read_text())
assert s['argv'][1:]==['corrected.dsn','-o','out.ses'] and s['exit_code']==0 and not s['outer_timeout'] and s['outer_limit_seconds']==1800
assert s['ses_exists'] and not (E/'processes/main').exists() and not json.loads((E/'smoke-gate.json').read_text())['main_allowed']
assert a['router_attempts']==dict(smoke=1,main=0) and a['stage_0']['unrouted_count']==1
assert all(v is None for v in a['stage_0']['four_metrics'].values())
assert all(v is None for v in a['stage_1']['four_metrics'].values())
d=json.loads((E/'processes/smoke-import/drc.json').read_text());assert len(d['unconnected_items'])==1 and not d['violations']
assert w['width_histogram_mm']=={'0.2':1} and w['paths_below_020mm']==0 and w['paths']==1
assert a['stage_0']['diagnostic_only']['returned_copper_equals_original']
for f,info in s['files'].items():assert hashlib.sha256((E/'processes/smoke'/f).read_bytes()).hexdigest()==info['sha256']
for f,h in json.loads((E/'source-manifest.json').read_text()).items():assert hashlib.sha256((ROOT/'.issue107-runtime/archive-source'/f).read_bytes()).hexdigest()==h
for f,h in json.loads((E/'oracle-hashes.json').read_text()).items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h
for p in E.rglob('*'):
 if p.is_file():
  assert p.read_bytes()[:4]!=b'\x7fELF',p
  if p.suffix=='.py':ast.parse(p.read_text())
assert not list(E.rglob('*.cmd'))
r=dict(verified_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),baseline_files_unchanged=len(rows),router_invocations=dict(smoke=1,main=0),smoke_expected_acceptance_failure=True,unrouted_count=1,four_metrics_all_null=True,saved_ses_hash_verified=True,widths_verified=True,source_and_oracles_unchanged=True,no_elf_binary=True,no_command_files=True,python_syntax_valid=True)
(E/'verification.json').write_text(json.dumps(r,indent=2)+'\n')
files={str(p.relative_to(E)):hashlib.sha256(p.read_bytes()).hexdigest() for p in E.rglob('*') if p.is_file() and p.name!='manifest.json'}
files['../../../../../docs/issue-107-topola-falsification.md']=hashlib.sha256((ROOT/'docs/issue-107-topola-falsification.md').read_bytes()).hexdigest()
(E/'manifest.json').write_text(json.dumps(files,indent=2)+'\n');print(json.dumps(r,indent=2))
