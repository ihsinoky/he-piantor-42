"""Issue 155 audited runner; writable runtime confined to .issue155-runtime."""
from pathlib import Path
import os,sys,json,hashlib,datetime,time,subprocess
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[4];E=Path(__file__).resolve().parent;T=R/'.issue155-runtime';B=R/'.issue129-runtime';K=T/'KiCadRoutingTools'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
env={k:v for k,v in os.environ.items() if k not in ['DISPLAY','WAYLAND_DISPLAY']}
env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(B/'kicad/usr/lib/python3/dist-packages')+':'+str(B/'geometry/lib/python3.12/site-packages'),LD_LIBRARY_PATH=str(B/'kicad/usr/lib/x86_64-linux-gnu')+':'+str(B/'kicad/usr/lib/kicad'),KICAD_STOCK_DATA_HOME=str(B/'kicad/usr/share/kicad'),KICAD_CLI=str(B/'kicad/usr/bin/kicad-cli'),TMPDIR=str(T/'tmp'),BUN_INSTALL_CACHE_DIR=str(T/'bun-cache'))
for k in ['CONFIG','CACHE','DATA','STATE']:env['XDG_'+k+'_HOME']=str(T/k.lower())
for k in ['tmp','config','cache','data','state']:(T/k).mkdir(exist_ok=True)
env['PATH']=str(B/'venv/bin')+':'+str(B/'kicad/usr/bin')+':'+os.environ['PATH']
ARGS=['--escalation','off','--track-width','0.1','--clearance','0.1','--via-size','0.6','--via-drill','0.3','--layers','F.Cu','In1.Cu','In2.Cu','B.Cu','--layer-costs','1.0','-1','1.0','1.0']
def run(name,argv,cwd=R,timeout=1800):
 w=E/'processes'/name;w.mkdir(parents=True,exist_ok=False);start=now();t=time.monotonic()
 save(w/'launch.json',dict(argv=list(map(str,argv)),cwd=str(cwd),start_utc=start,timeout_seconds=timeout))
 with (w/'stdout').open('w') as a,(w/'stderr').open('w') as b:
  proc=subprocess.Popen(list(map(str,argv)),cwd=cwd,env=env,stdout=a,stderr=b,start_new_session=True)
  try:rc=proc.wait(timeout);expired=False
  except subprocess.TimeoutExpired:
   import signal
   os.killpg(proc.pid,signal.SIGTERM)
   try:proc.wait(15)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
   rc=proc.returncode;expired=True
 save(w/'record.json',dict(argv=list(map(str,argv)),cwd=str(cwd),start_utc=start,end_utc=now(),elapsed_seconds=time.monotonic()-t,exit_code=rc,timed_out=expired,timeout_seconds=timeout,env_overrides={k:env[k] for k in ['PYTHONPATH','LD_LIBRARY_PATH','TMPDIR','KICAD_CLI','BUN_INSTALL_CACHE_DIR']},display_unset=True))
 print(name,rc,flush=True);return rc
if __name__=='__main__':
 if len(sys.argv)>1:sys.exit(run(sys.argv[1],sys.argv[2:]))
