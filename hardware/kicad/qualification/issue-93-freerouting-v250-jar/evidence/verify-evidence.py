#!/usr/bin/env python3
"""Read-only checks of submitted hashes, gates, input immutability and change scope."""
import gzip,hashlib,json,pathlib,re,subprocess
E=pathlib.Path(__file__).resolve().parent;R=E.parents[4]
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['smoke','run-1']:
 p=E/'processes'/name;r=json.loads((p/'record.json').read_text())
 assert r['exit_code']==0 and not r['timed_out']
 assert r['input_sha256']==r['input_sha256_after']==h(p/'input.dsn')
 for n,digest in r['artifacts'].items():assert h(p/n)==digest,(name,n)
 assert (p/'user-data/freerouting.json').exists()
 assert (p/'output.ses').exists()
 assert not (p/'stderr').read_text()
base=R/'hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/processes/main-initial-route';b=json.loads((base/'record.json').read_text())
for n in ['stdout','stderr']:assert h(base/n)==b[n+'_sha256']
for a in b['artifacts']:
 f=base/a['label'];raw=f.read_bytes() if f.exists() else gzip.decompress(pathlib.Path(str(f)+'.gz').read_bytes());assert hashlib.sha256(raw).hexdigest()==a['sha256']
assert json.loads((E/'smoke-gate.json').read_text())['allowed']
assert not json.loads((E/'run-2-gate.json').read_text())['allowed']
assert not (E/'processes/run-2').exists()
a=json.loads((E/'assessment.json').read_text());assert all(v is None for v in a['physical_metrics'].values())
assert a['router_invocations']==dict(smoke=1,main_run_1=1,main_run_2=0)
for d in json.loads((E/'official/distribution.json').read_text()):assert d['match'] and h(pathlib.Path(d['path']))==d['sha256']==d['official_sha256']
changes=subprocess.check_output(['git','diff','--name-only','origin/main'],cwd=R,text=True).splitlines()
assert all(n=='docs/issue-93-freerouting-v250-jar-reevaluation.md' or n.startswith('hardware/kicad/qualification/issue-93-freerouting-v250-jar/') for n in changes),changes
for doc in [R/'docs/issue-93-freerouting-v250-jar-reevaluation.md']:
 for target in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
  if '://' not in target:assert (doc.parent/target.split('#')[0]).exists(),target
print('PASS: new run artifact hashes, fixed inputs, baseline raw/SES/settings hashes, official distribution digests, conditional gates, null metrics, document links, existing tracked files unchanged.')
