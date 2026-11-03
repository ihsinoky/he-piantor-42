"""Issue #91 bounded runner. Invoke only for authorized run-1 / gated run-2."""
import datetime, hashlib, json, os, pathlib, shutil, subprocess, sys, time
root=pathlib.Path(__file__).resolve().parent
run=sys.argv[1]
assert run in ('run-1','run-2')
d=root/'processes'/run
assert not d.exists(), 'Never overwrite or repeat a run'
d.mkdir(parents=True)
source=root.parents[1]/'issue-87-native-main-routing/resume-01/evidence/processes/main-restore/corrected.dsn'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert h(source)=='75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2'
shutil.copyfile(source,d/'input.dsn')
if run=='run-2':
 gate=json.loads((root/'run-2-gate.json').read_text()); assert gate['authorized'] is True
cmd=['/home/hatch/workspace/tools/freerouting-2.5.0/freerouting-cli',f'--user_data_path={d}/user-data','--gui.enabled=false','--api_server.enabled=false','-da','--profile.allow_telemetry=false','--router.automatic_neckdown=false','--router.max_threads=1',f'--router.optimizer.enabled={str(run=="run-2").lower()}',f'--router.fanout.enabled={str(run=="run-2").lower()}','--router.job_timeout=00:20:00','-mp','100','-mt','0','-is','sequential','-de',str(d/'input.dsn'),'-do',str(d/'output.ses'),f'--router.result_json={d}/result.json']
env={k:v for k,v in os.environ.items() if not k.startswith('FREEROUTING__') and k!='DISPLAY'}
env.update(LANG='C.UTF-8',LC_ALL='C.UTF-8',TZ='UTC')
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
record={'command':cmd,'cwd':str(d),'start_utc':now(),'timeout_seconds':1260,'env_overrides':{'LANG':'C.UTF-8','LC_ALL':'C.UTF-8','TZ':'UTC'},'display_unset':True,'freerouting_environment_removed':True,'input_sha256':h(d/'input.dsn')}
(d/'record.json').write_text(json.dumps(record,indent=2)+'\n')
start=time.monotonic()
with (d/'stdout').open('wb') as out,(d/'stderr').open('wb') as err:
 p=subprocess.Popen(cmd,cwd=d,env=env,stdout=out,stderr=err,start_new_session=True)
 try: code=p.wait(timeout=1260); timed_out=False
 except subprocess.TimeoutExpired:
  import signal
  os.killpg(p.pid,signal.SIGTERM)
  try:p.wait(timeout=10)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
  code=p.returncode;timed_out=True
record.update(end_utc=now(),elapsed_seconds=time.monotonic()-start,exit_code=code,timed_out=timed_out,stdout_sha256=h(d/'stdout'),stderr_sha256=h(d/'stderr'))
record['artifacts']=[{'path':str(f.relative_to(root)),'sha256':h(f)} for f in sorted(d.rglob('*')) if f.is_file() and f.name not in ('record.json',)]
(d/'record.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items() if k not in ('command','artifacts')}))
