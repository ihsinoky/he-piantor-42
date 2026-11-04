import runpy,shutil,subprocess
from pathlib import Path
E=Path(__file__).resolve().parent;globals().update(runpy.run_path(str(E/'prepare-inputs.py')))
D=E/'configuration';D.mkdir(exist_ok=True);diffs={}
def delta(a,b,path=''):
 if isinstance(a,dict) and isinstance(b,dict):
  rows=[]
  for k in sorted(set(a)|set(b)):
   if k not in a or k not in b:rows.append(dict(path=path+'/'+k,before=a.get(k),after=b.get(k)))
   else:rows.extend(delta(a[k],b[k],path+'/'+k))
  return rows
 return [] if a==b else [dict(path=path,before=a,after=b)]
for stage in ['smoke','main']:
 for policy in ['default','off']:
  assert run(stage+'-readback-v2-'+policy,[TMP/'venv/bin/python3',E/'read-effective.py',D/f'{stage}-{policy}.json',stage,policy],R)==0
 a=json.loads((D/f'{stage}-default.json').read_text());b=json.loads((D/f'{stage}-off.json').read_text())
 for x in [a,b]:
  for k in ['checked_utc','policy']:x.pop(k)
 diffs[stage]=delta(a,b)
 assert {x['path'] for x in diffs[stage]}=={'/cli_namespace/escalation','/escalation_policy'}
save(D/'diff.json',dict(checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),only_escalation_diff=True,differences=diffs,baseline='Replayed #113 bare CLI resolver against identical frozen inputs with identical version/runtime; aborted before routing. #113 did not save a full configuration dump.',source_unmodified=True))
for name in ['binary-provenance.json','inspection-runtime-hashes.json','reused-kicad-package-hashes.json','source-manifest.json','source-provenance.json']:
 shutil.copyfile(R/'hardware/kicad/qualification/issue-113-kicad-routing-tools-falsification/evidence'/name,E/('reused-'+name))
