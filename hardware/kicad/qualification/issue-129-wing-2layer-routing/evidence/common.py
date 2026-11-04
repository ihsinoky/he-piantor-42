"""Evidence runner; all temporary state lives below the workspace runtime."""
from pathlib import Path
import os,json,hashlib,datetime,time,subprocess
R=Path(__file__).resolve().parents[5];E=Path(__file__).resolve().parent;T=R/'.issue129-runtime'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
env={k:v for k,v in os.environ.items() if k not in ['DISPLAY','WAYLAND_DISPLAY']}
env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(T/'kicad/usr/lib/python3/dist-packages')+':'+str(T/'geometry/lib/python3.12/site-packages'),LD_LIBRARY_PATH=str(T/'kicad/usr/lib/x86_64-linux-gnu')+':'+str(T/'kicad/usr/lib/kicad'),KICAD_STOCK_DATA_HOME=str(T/'kicad/usr/share/kicad'),KICAD_CLI=str(T/'kicad/usr/bin/kicad-cli'),TMPDIR=str(T/'tmp'),BUN_INSTALL_CACHE_DIR=str(T/'bun-cache'))
for k in ['CONFIG','CACHE','DATA','STATE']:env['XDG_'+k+'_HOME']=str(T/k.lower())
for k in ['tmp','config','cache','data','state']: (T/k).mkdir(exist_ok=True)
env['PATH']=str(T/'venv/bin')+':'+str(T/'kicad/usr/bin')+':'+os.environ['PATH']
def run(name,argv,cwd=R,timeout=1800):
 w=E/'processes'/name;w.mkdir(parents=True,exist_ok=False);start=now();t=time.monotonic()
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
if __name__=='__main__':save(E/'runtime-environment.json',{k:v for k,v in env.items() if k in ['PYTHONPATH','LD_LIBRARY_PATH','TMPDIR','KICAD_STOCK_DATA_HOME','PATH'] or k.startswith('XDG_')})
