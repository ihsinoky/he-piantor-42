"""Verify evidence, exact single-condition argv, smoke gate, hashes and added-only scope."""
import datetime,hashlib,json,pathlib,subprocess
E=pathlib.Path(__file__).resolve().parent; ROOT=E.parents[4]
G=['git','--git-dir=/tmp/issue-99-fastroute/git','--work-tree='+str(ROOT)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads((E/p).read_text())
expected={'smoke':'7214a0299ce19fae8163fa82a7d844e71c5bbf43b077392cfff7c7b5a9d1f3e9','main':'75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2'}
for stage in ['smoke','main']:
 rec=read('processes/'+stage+'/record.json');work=E/'processes'/stage
 assert rec['argv']==['/tmp/issue-99-fastroute/fastroute-0.1.14-linux-x64/fastroute','-de','corrected.dsn','-do','out.ses','--report=report.json','--max-time=1800','--router.min_trace_width_um=200']
 assert rec['exit_code']==0 and not rec.get('outer_timeout') and rec['input_unchanged']
 assert rec['environment']['DISPLAY'] is None and rec['environment']['WAYLAND_DISPLAY'] is None
 assert rec['binary_sha256']=='a4efebd6bfbb6614c9bac0535441dd65983d1a8e2cb3e00ebcf3ce90f2757d9f'
 assert sha(work/'corrected.dsn')==expected[stage]
 source=ROOT/'hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/processes'/('smoke-restore' if stage=='smoke' else 'main-restore')/'corrected.dsn'
 assert sha(source)==expected[stage]
 for name,meta in rec['artifacts'].items():assert sha(work/name)==meta['sha256'] and (work/name).stat().st_size==meta['bytes']
 assert read(stage+'-ses-inspection.json')['ses_sha256']==sha(work/'out.ses')
smoke=read('smoke-independent.json')
assert all(smoke[k]==0 for k in ['required_unconnected','wrong_net_actual_copper_contacts','targeted_material_violations','unexplained_transfer_changes'])
assert read('smoke-ses-inspection.json')['paths_below_020mm']==0
assert read('smoke-gate.json')['main_allowed']
assert read('smoke-gate.json')['validated_utc']<read('processes/main/record.json')['start_utc']
a=read('assessment.json');stats=read('processes/main/report.json')['stats']
if stats['unrouted']:
 assert all(v is None for v in a['independent_metrics'].values())
 assert not (E/'processes/main-import').exists()
 assert a['verdict']=='FIXED_CONDITION_FAIL'
for p,h in read('oracle-hashes.json').items():assert sha(ROOT/p)==h
for row in read('baseline-verification.json'):assert sha(ROOT/row['path'])==row['sha256']
assert read('installation.json')['official_checksum_match'] and read('installation.json')['reverified_current_official_checksums']
# All staged changes must be additions under the two authorized destinations.
changes=subprocess.check_output(G+['diff','--cached','--name-status','origin/main'],text=True).splitlines()
assert changes
for line in changes:
 status,path=line.split('\t');assert status=='A',line
 assert path=='docs/issue-99-fastroute-width-floor.md' or path.startswith('hardware/kicad/qualification/issue-99-fastroute-width-floor/'),path
 data=(ROOT/path).read_bytes();assert not data.startswith(b'\x7fELF') and not path.endswith(('.deb','.tar.gz','.zip'))
assert subprocess.check_output(G+['diff','--name-only'],text=True)==''
assert subprocess.check_output(G+['branch','--show-current'],text=True).strip()=='issue-99-fastroute-width-floor'
assert subprocess.check_output(G+['merge-base','HEAD','origin/main'],text=True).strip()==read('start.json')['base_commit']
now=datetime.datetime.now(datetime.timezone.utc);deadline=datetime.datetime.fromisoformat(read('start.json')['deadline_utc']);assert now<deadline
result=dict(status='PASS',checked_utc=now.isoformat(),staged_added_files=len(changes),exact_argv=True,smoke_gate_before_main=True,hashes_match=True,main_metrics_null_when_unrouted=True,additions_only=True,no_binary=True,within_two_hour_timebox=True)
(E/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
