"""Freeze historical inputs and rerun the independent Issue 87 reconciliation."""
import os,json,hashlib,subprocess,shutil,time,datetime
from pathlib import Path
R=Path.cwd(); E=R/'hardware/kicad/qualification/issue-115-kicad-routing-tools-escalation-off/evidence'; P=R/'hardware/kicad/qualification/issue-87-native-main-routing'; OLD=P.parent/'eda-004g/resume-02'; RT=R/'.issue105-runtime'; TMP=R/'.issue113-runtime'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
env=dict(PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(RT/'kicad/usr/lib/python3/dist-packages')+':'+str(RT/'geometry/lib/python3.12/site-packages'),LD_LIBRARY_PATH=str(RT/'kicad/usr/lib/x86_64-linux-gnu')+':'+str(RT/'kicad/usr/lib/kicad'),KICAD_STOCK_DATA_HOME=str(RT/'kicad/usr/share/kicad'))
env['KICAD_CLI']=str(RT/'kicad/usr/bin/kicad-cli')
env['PATH']=str(TMP/'venv/bin')+':'+str(RT/'kicad/usr/bin')+':'+os.environ['PATH']
for k in ['CONFIG','CACHE','DATA','STATE']:env['XDG_'+k+'_HOME']=str(TMP/k.lower())
save(E/'kicad-env.json',env)
def run(name,args,cwd=None,timeout=120):
 w=E/'processes'/name;w.mkdir(parents=True,exist_ok=False);start=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic();e=os.environ.copy();e.update(env);e.pop('DISPLAY',None);e.pop('WAYLAND_DISPLAY',None)
 with (w/'stdout').open('w') as a,(w/'stderr').open('w') as b:
  try:p=subprocess.run(list(map(str,args)),cwd=cwd or R,env=e,stdout=a,stderr=b,timeout=timeout);rc=p.returncode;expired=False
  except subprocess.TimeoutExpired:rc=None;expired=True
 save(w/'record.json',dict(argv=list(map(str,args)),cwd=str(cwd or R),start_utc=start,end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-t,exit_code=rc,timed_out=expired,timeout_seconds=timeout,env_overrides=env,display_unset=True))
 print(name,rc,flush=True);return rc
if __name__=='__main__':
 sources={};checks={}
 for stage in ['smoke','main']:
  w=E/'inputs'/stage;w.mkdir(parents=True)
  for name in ['main.kicad_pcb','main.kicad_pro','corrected.dsn']:
   origin=R/'hardware/kicad/qualification/issue-113-kicad-routing-tools-falsification/evidence/inputs'/stage/name
   shutil.copyfile(origin,w/name);sources[str((w/name).relative_to(E))]=dict(source=str(origin.relative_to(R)),sha256=digest(w/name))
  assert digest(w/'main.kicad_pcb')=={'main':'46676e57e9618940a33c5e298244e97aaec61498a87aa7c58a264e444fc71e20','smoke':'3f70465774f577ffe803f88de017004d164f045e6415ade22766a461a2454bec'}[stage]
  assert digest(w/'main.kicad_pro')=='a5bc2aea160cc9a8b3035f77f0167c26a1de7ffdb749740c94fb7a9e9a3c87d5'
  assert run(stage+'-read-input',['/usr/bin/python3',OLD/'read-pcb.py',w/'main.kicad_pcb',w/'snapshot.json'])==0
  snap=json.loads((w/'snapshot.json').read_text());assert snap==json.loads((origin.parent/'snapshot.json').read_text())
  assert snap['layers']==2 and snap['rules']['m_MinClearance']==snap['rules']['m_TrackMinWidth']==snap['default']['clearance']==snap['default']['width']==.2
  effective=P/'resume-01/evidence/processes'/f'{stage}-read-corrected/effective.json'
  assert run(stage+'-dsn-equivalence',['/usr/bin/python3',P/'resume-01/check-dsn.py',stage,w/'corrected.dsn',w/'snapshot.json',effective,E/f'{stage}-dsn-equivalence.json'])==0
  checks[stage]=dict(pass_equivalence=True,pcb_sha256=digest(w/'main.kicad_pcb'),project_sha256=digest(w/'main.kicad_pro'))
 save(E/'input-provenance.json',sources)
 assert run('native-inventory',['/usr/bin/python3',E/'check-native-inventory.py'])==0
 save(E/'equivalence-gate.json',dict(pass_equivalence=True,checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),inputs=checks,native_inventory=json.loads((E/'native-inventory.json').read_text()),all_items_completed_before_routing=True))
