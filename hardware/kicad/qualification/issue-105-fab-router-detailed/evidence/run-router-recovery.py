"""Single-shot staged DSN harness. Refuses reruns and requires a passing smoke gate."""
import datetime,hashlib,json,os,pathlib,shutil,subprocess,sys,time
E=pathlib.Path(__file__).resolve().parent;ROOT=E.parents[4];T=pathlib.Path('/tmp/issue-105-fab-router')
stage=sys.argv[1];assert stage in ('smoke','main')
if stage=='main':
 config=json.loads((E/'settings-comparison-before-main.json').read_text());assert config['main_allowed_configuration'] is True
 assert config['changed_fields']=={'detailedRouter':{'before':'off','after':'tiles'}}
 gate=json.loads((E/'smoke-gate.json').read_text());assert gate['main_allowed'] is True
 independent=json.loads((E/'smoke-independent.json').read_text())
 for key in ['required_unconnected','wrong_net_actual_copper_contacts','targeted_material_violations','unexplained_transfer_changes']:assert independent[key]==0
 assert json.loads((E/'processes/smoke/check-drc-after.json').read_text())['counts']==dict(violations=0,incompletes=0)
work=E/'processes'/stage;work.mkdir(parents=True,exist_ok=False)
source=ROOT/'hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/processes'/(stage+'-restore')/'corrected.dsn'
expected={'smoke':'7214a0299ce19fae8163fa82a7d844e71c5bbf43b077392cfff7c7b5a9d1f3e9','main':'75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2'}[stage]
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert h(source)==expected;shutil.copyfile(source,work/'corrected.dsn')
argv=[str(T/'bun/bun-linux-x64/bun'),'run',str(E/'driver.ts'),str(T/'fab_router'),str(work/'corrected.dsn'),str(work)]
env=os.environ.copy();env.pop('DISPLAY',None);env.pop('WAYLAND_DISPLAY',None);env['BUN_INSTALL_CACHE_DIR']=str(ROOT/'.issue105-runtime/bun-cache')
record=dict(argv=argv,cwd=str(ROOT),stage=stage,input_sha256=expected,start_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),external_timeout_seconds=1920,headless=True)
(E/(stage+'-recovery-launch.json')).write_text(json.dumps(record,indent=2)+'\n');t=time.monotonic()
with (work/'stdout').open('wb') as out,(work/'stderr').open('wb') as err:
 try:r=subprocess.run(argv,cwd=ROOT,env=env,stdout=out,stderr=err,timeout=1920);record['exit_code']=r.returncode;record['external_timeout']=False
 except subprocess.TimeoutExpired:record.update(exit_code=None,external_timeout=True)
record.update(elapsed_seconds=time.monotonic()-t,end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files={p.name:dict(bytes=p.stat().st_size,sha256=h(p)) for p in work.iterdir() if p.is_file()})
assert h(source)==h(work/'corrected.dsn')==expected
(work/'record.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
