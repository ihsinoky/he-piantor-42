"""One default headless attempt per stage, with an outer 1800-second limit."""
import datetime,hashlib,json,os,pathlib,shutil,signal,subprocess,sys,time
E=pathlib.Path(__file__).resolve().parent; ROOT=E.parents[4]
stage=sys.argv[1]; assert stage in ('smoke','main')
if stage=='main':
 gate=json.loads((E/'smoke-gate.json').read_text()); assert gate['main_allowed']
work=E/'processes'/stage; work.mkdir(parents=True,exist_ok=False)
source=ROOT/'hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/processes'/(stage+'-restore')/'corrected.dsn'
expected=json.loads((E/'input-hashes.json').read_text())[stage]['sha256']
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
shutil.copyfile(source,work/'corrected.dsn')
binary=pathlib.Path('/tmp/issue-107-topola/cargo/bin/topola'); assert binary.is_file()
env=os.environ.copy(); env.pop('DISPLAY',None); env.pop('WAYLAND_DISPLAY',None)
argv=[str(binary),'corrected.dsn','-o','out.ses']; start=time.monotonic()
rec=dict(stage=stage,argv=argv,cwd=str(work),start_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),outer_limit_seconds=1800,input_sha256=expected,binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),display=None,wayland_display=None,stdin='DEVNULL',default_options=True)
(E/(stage+'-launch.json')).write_text(json.dumps(rec,indent=2)+'\n')
with (work/'stdout').open('wb') as out,(work/'stderr').open('wb') as err:
 p=subprocess.Popen(argv,cwd=work,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err,start_new_session=True)
 try: p.wait(timeout=1800); timeout=False
 except subprocess.TimeoutExpired:
  timeout=True; os.killpg(p.pid,signal.SIGTERM)
  try:p.wait(timeout=5)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
rec.update(exit_code=p.returncode,outer_timeout=timeout,elapsed_seconds=time.monotonic()-start,end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),ses_exists=(work/'out.ses').exists(),files={f.name:dict(bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in work.iterdir() if f.is_file()})
assert hashlib.sha256((work/'corrected.dsn').read_bytes()).hexdigest()==expected
(work/'record.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec,indent=2))
