"""Issue226 runner; all scratch confined to .issue226-runtime."""
from pathlib import Path
import os,sys,json,hashlib,datetime,time,subprocess
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[4];E=Path(__file__).resolve().parent;T=R/'.issue226-runtime';BASE=Path('/home/hatch/workspace/projects/he-piantor-42');B=BASE/'.issue129-runtime'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
env={k:v for k,v in os.environ.items() if k not in ['DISPLAY','WAYLAND_DISPLAY']}
env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(B/'kicad/usr/lib/python3/dist-packages')+':'+str(B/'geometry/lib/python3.12/site-packages'),LD_LIBRARY_PATH=str(B/'kicad/usr/lib/x86_64-linux-gnu')+':'+str(B/'kicad/usr/lib/kicad'),KICAD_STOCK_DATA_HOME=str(B/'kicad/usr/share/kicad'),KICAD_CLI=str(B/'kicad/usr/bin/kicad-cli'),TMPDIR=str(T/'tmp'))
for k in ['CONFIG','CACHE','DATA','STATE']:env['XDG_'+k+'_HOME']=str(T/k.lower())
for k in ['tmp','config','cache','data','state']:(T/k).mkdir(exist_ok=True)
def run(name,argv,cwd=R,timeout=1800):
 w=E/'processes'/name;w.mkdir(parents=True,exist_ok=False);start=now();t=time.monotonic()
 with (w/'stdout').open('w') as a,(w/'stderr').open('w') as b:
  try:rc=subprocess.run(list(map(str,argv)),cwd=cwd,env=env,stdout=a,stderr=b,timeout=timeout).returncode
  except subprocess.TimeoutExpired:rc=124
 save(w/'record.json',dict(argv=list(map(str,argv)),cwd=str(cwd),start_utc=start,end_utc=now(),elapsed_seconds=time.monotonic()-t,exit_code=rc,timeout_seconds=timeout))
 print(name,rc,flush=True);return rc
if __name__=='__main__':sys.exit(run(sys.argv[1],sys.argv[2:]))
