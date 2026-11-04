"""Issue 117 evidence helpers; all processes logged and headless."""
import os, sys, json, hashlib, subprocess, time, datetime
from pathlib import Path
sys.dont_write_bytecode=True
E=Path(__file__).resolve().parent
R=E.parents[4]
RT=R/'.issue105-runtime'
KRT=R/'.issue113-runtime/KiCadRoutingTools'
FAB=RT/'fab_router'
GIT='/tmp/issue-119-main/git'
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
env=json.loads((R/'hardware/kicad/qualification/issue-115-kicad-routing-tools-escalation-off/evidence/kicad-env.json').read_text())
env['PATH']=str(R/'.issue113-runtime/venv/bin')+':'+str(RT/'kicad/usr/bin')+':'+os.environ['PATH']
for k in ['CONFIG','CACHE','DATA','STATE']:env['XDG_'+k+'_HOME']='/tmp/issue-119-main/'+k.lower()
def run(name,args,cwd=None,timeout=120):
 w=E/'processes'/name;w.mkdir(parents=True,exist_ok=False)
 e=os.environ.copy();e.update(env);e.pop('DISPLAY',None);e.pop('WAYLAND_DISPLAY',None)
 t=time.monotonic();record=dict(argv=list(map(str,args)),cwd=str(cwd or R),start_utc=utc(),timeout_seconds=timeout,env_overrides=env,headless=True)
 save(w/'launch.json',record)
 with (w/'stdout').open('w') as a,(w/'stderr').open('w') as b:
  try:p=subprocess.run(list(map(str,args)),cwd=cwd or R,env=e,stdout=a,stderr=b,timeout=timeout);rc=p.returncode;expired=False
  except subprocess.TimeoutExpired:rc=None;expired=True
 record.update(exit_code=rc,timed_out=expired,end_utc=utc(),elapsed_seconds=time.monotonic()-t)
 save(w/'record.json',record);print(name,rc,flush=True);return rc
def delta(a,b,path=''):
 if isinstance(a,dict) and isinstance(b,dict):
  rows=[]
  for k in sorted(set(a)|set(b)):
   if k not in a or k not in b:rows.append(dict(path=path+'/'+k,before=a.get(k),after=b.get(k)))
   else:rows.extend(delta(a[k],b[k],path+'/'+k))
  return rows
 return [] if a==b else [dict(path=path,before=a,after=b)]
