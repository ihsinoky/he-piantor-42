"""Verify submitted evidence without rerunning the router."""
import pathlib,json,hashlib,subprocess,datetime,ast
E=pathlib.Path(__file__).resolve().parent;ROOT=E.parents[4];G=['git','--git-dir=/tmp/issue-101-freerouting-cpp/git','--work-tree='+str(ROOT)]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
base=read(E/'baseline-verification.json')['base']; rows=subprocess.check_output(G+['ls-tree','-r',base]).decode().splitlines()
for row in rows:
 meta,name=row.split('\t'); assert subprocess.check_output(['git','hash-object',str(ROOT/name)]).decode().strip()==meta.split()[2],name
for p,h in read(E/'oracle-hashes.json').items(): assert sha(ROOT/p)==h
for name,h in read(E/'source-manifest.json').items(): assert sha(ROOT/'.issue101-runtime'/name)==h,name
for p in E.glob('*.py'): ast.parse(p.read_text())
for stage in ('smoke','main'):
 p=E/'processes'/stage/'record.json'
 if not p.exists(): continue
 rec=read(p); assert rec['argv'][1:]==['--autoroute','corrected.dsn'];assert rec['input_unchanged']
 assert rec['environment']['DISPLAY'] is None and rec['environment']['WAYLAND_DISPLAY'] is None
 for name,info in rec['artifacts'].items(): assert sha(p.parent/name)==info['sha256']
 if stage=='main':
  gate=read(E/'smoke-gate.json'); assert gate['main_allowed'];assert gate['validated_utc']<rec['start_utc']
  checks=read(E/'smoke-independent.json'); assert all(checks[k]==0 for k in ['required_unconnected','wrong_net_actual_copper_contacts','targeted_material_violations','unexplained_transfer_changes'])
a=read(E/'assessment.json')
if a['verdict']=='STAGE0_FAIL':
 assert not (E/'processes/main').exists(); assert a['main_invocations']==0
 assert not read(E/'smoke-gate.json')['main_allowed']
 smoke=read(E/'processes/smoke/record.json'); assert smoke['exit_code']==-11
 assert not (E/'processes/smoke/corrected.ses').exists()
 assert all(v is None for v in a['independent_metrics'].values())
 assert a['router_unrouted'] is None and not a['router_unrouted_measured']
if a.get('router_unrouted',0): assert all(v is None for v in a['independent_metrics'].values())
changes=subprocess.check_output(G+['diff','--cached','--name-status',base]).decode().splitlines()
for line in changes:
 status,name=line.split('\t'); assert status=='A'; assert name=='docs/issue-101-freerouting-cpp-falsification.md' or name.startswith(str(E.relative_to(ROOT).parent)+'/')
for p in E.rglob('*'):
 if p.is_file(): assert p.read_bytes()[:4]!=b'\x7fELF',str(p)
now=datetime.datetime.now(datetime.timezone.utc); assert now<datetime.datetime.fromisoformat(read(E/'timebox.json')['deadline_utc'])
r=dict(status='PASS',baseline_files_unchanged=len(rows),official_source_files_unchanged=len(read(E/'source-manifest.json')),added_only=True,binary_not_submitted=True,input_hashes_unchanged=True,strict_router_argv=True,checked_utc=now.isoformat())
(E/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
