#!/usr/bin/env python3
"""Issue 93 bounded, unmodified official JAR invocation. One invocation per directory."""
import datetime,hashlib,json,os,pathlib,shutil,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parent
REPO=pathlib.Path(__file__).resolve().parents[5]
name=sys.argv[1];assert name in ('smoke','run-1','run-2')
p=ROOT/'processes'/name;assert not p.exists(), 'No retries';p.mkdir(parents=True);(p/'temp').mkdir();(p/'user-data').mkdir()
source=REPO/'hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/processes'/('smoke-restore' if name=='smoke' else 'main-restore')/'corrected.dsn'
expected='7214a0299ce19fae8163fa82a7d844e71c5bbf43b077392cfff7c7b5a9d1f3e9' if name=='smoke' else '75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2'
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
if name!='smoke':
 gate=json.loads((ROOT/('smoke-gate.json' if name=='run-1' else 'run-2-gate.json')).read_text());assert gate['allowed']
shutil.copyfile(source,p/'input.dsn')
t=pathlib.Path.home()/'workspace/tools/issue-93';java=next(t.glob('jdk-25*/bin/java'))
argv=[str(java),'-Djava.awt.headless=true','-Duser.language=en','-Duser.country=US','-Xmx2g',f'-Djava.io.tmpdir={p}/temp','-jar',str(t/'freerouting-2.5.0.jar'),f'--user_data_path={p}/user-data','--gui.enabled=false','--api_server.enabled=false','-da','--profile.allow_telemetry=false','--router.automatic_neckdown=false','--router.max_threads=1',f'--router.optimizer.enabled={str(name=="run-2").lower()}',f'--router.fanout.enabled={str(name=="run-2").lower()}','--router.job_timeout=00:20:00','-mp','100','-mt','0','-is','sequential','-de',str(p/'input.dsn'),'-do',str(p/'output.ses')]
env={k:v for k,v in os.environ.items() if k!='DISPLAY' and not k.startswith('FREEROUTING__')};env.update(LANG='C.UTF-8',LC_ALL='C.UTF-8',TZ='UTC')
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
record=dict(command=argv,cwd=str(p),start_utc=now(),input_sha256=expected,env_overrides={k:env[k] for k in ('LANG','LC_ALL','TZ')},display_unset=True,freerouting_env_unset=True,timeout_seconds=180 if name=='smoke' else 1260)
(p/'record.json').write_text(json.dumps(record,indent=2)+'\n');start=time.monotonic()
with (p/'stdout').open('w') as out,(p/'stderr').open('w') as err:
 proc=subprocess.Popen(argv,cwd=p,env=env,stdout=out,stderr=err);(p/'pid').write_text(str(proc.pid)+'\n')
 try:code=proc.wait(timeout=record['timeout_seconds']);record['timed_out']=False
 except subprocess.TimeoutExpired:
  proc.terminate()
  try:code=proc.wait(timeout=10)
  except subprocess.TimeoutExpired:proc.kill();code=proc.wait()
  record['timed_out']=True
record.update(end_utc=now(),elapsed_seconds=time.monotonic()-start,exit_code=code,input_sha256_after=hashlib.sha256((p/'input.dsn').read_bytes()).hexdigest())
record['artifacts']={str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file() and f.name not in ('record.json','pid')}
(p/'record.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
