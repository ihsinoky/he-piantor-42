"""Freeze historical inputs and rerun the independent Issue 87 reconciliation."""
import os,json,hashlib,subprocess,shutil,time,datetime
from pathlib import Path
R=Path.cwd(); E=R/'hardware/kicad/qualification/issue-113-kicad-routing-tools-falsification/evidence'; P=R/'hardware/kicad/qualification/issue-87-native-main-routing'; OLD=P.parent/'eda-004g/resume-02'; RT=R/'.issue105-runtime'; TMP=R/'.issue113-runtime'
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
 save(E/'start.json',dict(start_utc='2026-11-04T05:16:00Z',deadline_utc='2026-11-04T07:16:00Z',base='ce2d3803bec50d1c06546e44ca0736ef97d7de6d',base_files_byte_verified=7044,branch='issue-113-kicad-routing-tools-falsification',git_metadata='/tmp/issue-113-krt/git',reason='Original .git read-only; copied metadata, current repository work-tree, no existing file writes. cp ownership warnings did not affect contents.'))
 sources={};checks={}
 for name in ['smoke','main']:
  w=E/'inputs'/name;w.mkdir(parents=True)
  origin=P/'evidence/processes/smoke-read-before' if name=='smoke' else OLD/'evidence/processes/initial-author-pcb-explicit-public-library-io'
  for f in ['main.kicad_pcb','main.kicad_pro']:
   shutil.copyfile(origin/f,w/f);sources[str((w/f).relative_to(E))]=dict(source=str((origin/f).relative_to(R)),sha256=digest(w/f))
  dsn=P/'resume-01/evidence/processes'/f'{name}-restore/corrected.dsn';shutil.copyfile(dsn,w/'corrected.dsn')
  expect={'main':'75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2','smoke':'7214a0299ce19fae8163fa82a7d844e71c5bbf43b077392cfff7c7b5a9d1f3e9'}[name];assert digest(dsn)==expect
  sources[str((w/'corrected.dsn').relative_to(E))]=dict(source=str(dsn.relative_to(R)),sha256=expect)
  assert run(name+'-read-input',['/usr/bin/python3',OLD/'read-pcb.py',w/'main.kicad_pcb',w/'snapshot.json'])==0
  snap=json.loads((w/'snapshot.json').read_text());saved=P/'evidence/processes'/('smoke-read-before' if name=='smoke' else 'baseline-read')/'snapshot.json';assert snap==json.loads(saved.read_text())
  assert snap['layers']==2 and snap['rules']['m_MinClearance']==snap['rules']['m_TrackMinWidth']==snap['default']['clearance']==snap['default']['width']==.2
  effective=P/'resume-01/evidence/processes'/f'{name}-read-corrected/effective.json'
  rc=run(name+'-dsn-equivalence',['/usr/bin/python3',P/'resume-01/check-dsn.py',name,w/'corrected.dsn',w/'snapshot.json',effective,E/f'{name}-dsn-equivalence.json'])
  checks[name]=dict(pass_equivalence=rc==0,fresh_snapshot_matches_historical=True,signal_layers=2,footprints=len(snap['components']),physical_lands=len(snap['pads']),existing_tracks=len(snap['tracks']),pcb_sha256=digest(w/'main.kicad_pcb'),project_sha256=digest(w/'main.kicad_pro'))
 save(E/'input-provenance.json',sources);save(E/'equivalence-gate.json',dict(pass_equivalence=all(x['pass_equivalence'] for x in checks.values()),checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),inputs=checks))
