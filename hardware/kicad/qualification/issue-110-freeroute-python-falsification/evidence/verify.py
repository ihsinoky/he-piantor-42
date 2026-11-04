"""Verify additions-only evidence, immutable inputs, actual diagnostics and smoke gates."""
import ast,datetime,hashlib,json,pathlib,subprocess
E=pathlib.Path(__file__).resolve().parent;ROOT=E.parents[4];G=['git','--git-dir=/tmp/issue-110-freeroute/git','--work-tree='+str(ROOT)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pre=json.loads((E/'preexisting-files.json').read_text())
for f,h in pre.items():assert sha(ROOT/f)==h,f
base=json.loads((E/'baseline-verification.json').read_text())['base'];rows=subprocess.check_output(G+['ls-tree','-r',base],text=True).splitlines();names=[row.split('\t')[1] for row in rows]
actual=subprocess.check_output(G+['hash-object','--stdin-paths'],input='\n'.join(str(ROOT/f) for f in names)+'\n',text=True).splitlines();assert len(rows)==len(actual)
for row,h in zip(rows,actual):assert row.split('\t')[0].split()[2]==h,row
for f,h in json.loads((E/'oracle-hashes.json').read_text()).items():assert sha(ROOT/f)==h,f
pkg=next(pathlib.Path('/tmp/issue-110-freeroute/venv/lib').glob('python*/site-packages/freeroute'))
for f,h in json.loads((E/'source-manifest.json').read_text()).items():assert sha(pkg/f)==h
install=json.loads((E/'installation.json').read_text());assert sha(pathlib.Path('/tmp/issue-110-freeroute/dist')/install['distribution'])==install['sha256']
assert json.loads((E/'pip-report.json').read_text())['install'][0]['download_info']['archive_info']['hashes']['sha256']==install['sha256']
a=json.loads((E/'assessment.json').read_text())
for c in ['A','B']:
 d=E/c;rec=json.loads((d/'processes/smoke/record.json').read_text());gate=json.loads((d/'smoke-gate.json').read_text());m=json.loads((d/'smoke-measurement.json').read_text());width=json.loads((d/'smoke-ses-inspection.json').read_text());drc=json.loads((d/'processes/smoke-import/drc.json').read_text())
 argv=['corrected.dsn','--engine',('exact' if c=='A' else 'room')]+(['--pack'] if c=='B' else [])+['--shove','-do','out.ses'];assert rec['argv'][1:]==argv
 assert rec['exit_code']==0 and not rec['outer_timeout'] and rec['elapsed_seconds']<1800 and rec['ses_exists']
 assert not gate['main_allowed'] and not (d/'processes/main').exists()
 assert a['configurations'][c]['router_attempts']==dict(smoke=1,main=0)
 for f,info in rec['files'].items():assert sha(d/'processes/smoke'/f)==info['sha256']
 inputs=json.loads((E/'input-hashes.json').read_text());assert rec['input_sha256']==inputs['smoke']['sha256']
 for info in inputs.values():assert sha(ROOT/info['path'])==info['sha256']
 assert m['unrouted_count']==len(drc['unconnected_items'])==3
 assert len(drc['violations'])==4 and sum(v['type']=='track_width' for v in drc['violations'])==2
 assert width['paths']==width['paths_below_020mm']==2 and width['minimum_width_mm']==.02
 assert width['ses_sha256']==sha(d/'processes/smoke/out.ses')
 assert all(v is None for v in m['four_metrics'].values())
 assert all(v is None for v in a['configurations'][c]['stage_1']['four_metrics'].values())
 assert m['oracle_exit_code']==1 and not m['diagnostic_only']['source_local_copper_preserved']
 for process in ['ses-import','read-return','prepare-library','drc']:
  assert json.loads((d/f'processes/smoke-{process}/record.json').read_text())['exit_code']==0
assert (E/'A/processes/smoke/out.ses').read_bytes()==(E/'B/processes/smoke/out.ses').read_bytes()
for p in E.rglob('*'):
 if p.is_file():
  assert p.read_bytes()[:4]!=b'\x7fELF',p
  assert p.suffix not in ['.whl','.gz','.zip'],p
  if p.suffix=='.py':ast.parse(p.read_text())
changes=subprocess.check_output(G+['diff','--cached','--name-status',base],text=True).splitlines();assert changes
for line in changes:
 status,name=line.split('\t');assert status=='A' and (name=='docs/issue-110-freeroute-python-falsification.md' or name.startswith('hardware/kicad/qualification/issue-110-freeroute-python-falsification/')),line
now=datetime.datetime.now(datetime.timezone.utc);start=datetime.datetime.fromisoformat('2026-11-04T03:26:53+00:00');assert (now-start).total_seconds()<7200
result=dict(verified_utc=now.isoformat(),preexisting_files_unchanged=len(pre),latest_main_files_unchanged=len(rows),staged_additions_only=len(changes),router_attempts=dict(A=dict(smoke=1,main=0),B=dict(smoke=1,main=0)),gates_enforced=True,hashes_verified=True,diagnostic_counts_verified=True,null_policy_verified=True,no_distributions_or_binaries=True)
(E/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
(E/'submission.json').write_text(json.dumps(dict(before_commit_utc=now.isoformat(),elapsed_seconds=(now-start).total_seconds(),limit_seconds=7200),indent=2)+'\n')
files={str(p.relative_to(E)):sha(p) for p in E.rglob('*') if p.is_file() and p.name!='manifest.json'};files['../../../../../docs/issue-110-freeroute-python-falsification.md']=sha(ROOT/'docs/issue-110-freeroute-python-falsification.md');(E/'manifest.json').write_text(json.dumps(files,indent=2)+'\n');print(json.dumps(result,indent=2))
