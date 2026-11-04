"""Check saved evidence, unchanged existing files, and additions-only submission."""
import ast,datetime,hashlib,json,pathlib,subprocess
E=pathlib.Path(__file__).resolve().parent;ROOT=E.parents[4];G=['git','--git-dir=/tmp/issue-109-autoroute/git','--work-tree='+str(ROOT)]
pre=json.loads((E/'preexisting-files.json').read_text())
for f,h in pre.items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h,f
base=json.loads((E/'baseline-verification.json').read_text())['base'];rows=subprocess.check_output(G+['ls-tree','-r',base],text=True).splitlines();names=[row.split('\t')[1] for row in rows]
actual=subprocess.check_output(G+['hash-object','--stdin-paths'],input='\n'.join(str(ROOT/f) for f in names)+'\n',text=True).splitlines()
assert len(actual)==len(rows)
for row,h in zip(rows,actual):assert row.split('\t')[0].split()[2]==h,row
for f,h in json.loads((E/'oracle-hashes.json').read_text()).items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h
for f,h in json.loads((E/'source-manifest.json').read_text()).items():assert hashlib.sha256((ROOT/'.issue109-runtime/AutoRoute'/f).read_bytes()).hexdigest()==h
s=json.loads((E/'processes/smoke/record.json').read_text());a=json.loads((E/'assessment.json').read_text());gate=json.loads((E/'smoke-gate.json').read_text())
assert s['exit_code']==0 and not gate['main_allowed'] and not (E/'processes/main').exists()
assert a['stage_0']['unrouted_count']==2 and a['stage_0']['oracle_exit_code']==1
raw=a['stage_0']['diagnostic_only'];assert raw['original_tracks']==1 and raw['returned_tracks']==0 and not raw['source_local_copper_preserved']
assert raw['source_local_copper'][0]['missing_centerline_length_mm']==2.0
width=json.loads((E/'smoke-ses-inspection.json').read_text());assert width['paths']==0 and width['minimum_width_mm'] is None
assert s['argv'][1:]==['corrected.dsn','-o','out.ses','--check'] and not s['outer_timeout']
assert a['router_attempts']['smoke']==1 and a['router_attempts']['main']==int(gate['main_allowed'])
for stage in ['smoke','main']:
 p=E/'processes'/stage
 if not p.exists():continue
 rec=json.loads((p/'record.json').read_text());assert rec['argv'][1:]==['corrected.dsn','-o','out.ses','--check']
 for f,info in rec['files'].items():assert hashlib.sha256((p/f).read_bytes()).hexdigest()==info['sha256']
 meas=json.loads((E/(stage+'-measurement.json')).read_text());d=json.loads((E/'processes'/(stage+'-import')/'drc.json').read_text());assert meas['unrouted_count']==len(d['unconnected_items'])
 if rec['exit_code']==2 or meas['status']!='PASS':assert all(x is None for x in meas['four_metrics'].values())
for p in E.rglob('*'):
 if p.is_file():
  assert p.read_bytes()[:4]!=b'\x7fELF',p
  if p.suffix=='.py':ast.parse(p.read_text())
changes=subprocess.check_output(G+['diff','--cached','--name-status',base],text=True).splitlines()
for line in changes:
 status,name=line.split('\t');assert status=='A' and (name=='docs/issue-109-autoroute-falsification.md' or name.startswith('hardware/kicad/qualification/issue-109-autoroute-falsification/')),line
result=dict(verified_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),tracked_files_match_latest_main=len(rows),preexisting_files_unchanged=len(pre),router_attempts=a['router_attempts'],gate_enforced=True,saved_ses_and_input_hashes_verified=True,raw_kicad_count_verified=True,four_metrics_policy_verified=True,no_binary=True,source_and_oracles_unchanged=True,staged_changes_additions_only=len(changes))
(E/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
files={str(p.relative_to(E)):hashlib.sha256(p.read_bytes()).hexdigest() for p in E.rglob('*') if p.is_file() and p.name!='manifest.json'}
files['../../../../../docs/issue-109-autoroute-falsification.md']=hashlib.sha256((ROOT/'docs/issue-109-autoroute-falsification.md').read_bytes()).hexdigest()
(E/'manifest.json').write_text(json.dumps(files,indent=2)+'\n');print(json.dumps(result,indent=2))
