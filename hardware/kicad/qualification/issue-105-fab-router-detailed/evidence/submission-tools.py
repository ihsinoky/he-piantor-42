"""Create manifest and submission metadata from already-saved evidence; no routing."""
import datetime,hashlib,json,pathlib,subprocess,sys
E=pathlib.Path(__file__).resolve().parent;R=E.parents[4];T=pathlib.Path('/tmp/issue-105-fab-router');G=['git','--git-dir='+str(T/'git'),'--work-tree='+str(R)];load=lambda p:json.loads((E/p).read_text());now=datetime.datetime.now(datetime.timezone.utc)
assert now<datetime.datetime.fromisoformat(load('recovery-preflight.json')['deadline_utc'])
assert load('verification.json')['status']=='PASS'
allowed=['docs/issue-105-fab-router-detailed.md','hardware/kicad/qualification/issue-105-fab-router-detailed/']
subprocess.run(G+['add','--',*allowed],check=True)
changes=subprocess.check_output(G+['diff','--cached','--name-status','origin/main']).decode().splitlines()
assert changes
for line in changes:
 status,name=line.split('\t');assert status=='A' and (name==allowed[0] or name.startswith(allowed[1])),line
(E/'submission.json').write_text(json.dumps(dict(prepared_utc=now.isoformat(),resume_start_utc=load('recovery-preflight.json')['resume_start_utc'],deadline_utc=load('recovery-preflight.json')['deadline_utc'],elapsed_since_resume_seconds=(now-datetime.datetime.fromisoformat(load('recovery-preflight.json')['resume_start_utc'])).total_seconds(),branch='issue-105-fab-router-detailed',base_commit=load('recovery-preflight.json')['base_commit'],only_additions=True,scoped_files=len(changes),draft_requested=True,merge_authorized=False),indent=2)+'\n')
paths=[R/allowed[0]]+[p for p in E.parent.rglob('*') if p.is_file() and p.name!='manifest.json']
(E/'manifest.json').write_text(json.dumps({str(p.relative_to(R)):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(paths)},indent=2)+'\n')
subprocess.run(G+['add','--',*allowed],check=True);subprocess.run(G+['-c','core.whitespace=-blank-at-eof','diff','--cached','--check'],check=True)
# The preserved original geometry-install.log has a trailing blank line.
# Keep the raw evidence bytes; all other whitespace checks remain enabled.
print(json.dumps(dict(additive_scope='PASS',files=len(paths)+1,prepared_utc=now.isoformat())))
