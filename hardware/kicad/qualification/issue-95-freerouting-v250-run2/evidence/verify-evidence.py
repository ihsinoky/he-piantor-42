#!/usr/bin/env python3
"""Offline evidence checks; no router invocation or KiCad import."""
import hashlib,json,pathlib,subprocess
E=pathlib.Path(__file__).resolve().parent;R=E.parents[4]
hash_file=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
start=json.loads((E/'start.json').read_text())
for c in start['checks'].values():
 assert hash_file(pathlib.Path(c['path']))==c['sha256']==c['expected']
record=json.loads((E/'processes/run-2/record.json').read_text())
assert record['input_sha256']==record['input_sha256_after']==start['checks']['input']['sha256']
for rel,expected in record['artifacts'].items():
 assert hash_file(E/'processes/run-2'/rel)==expected,rel
for c in json.loads((E/'reference-integrity.json').read_text()):
 original=subprocess.check_output(['git','show',c['source_commit']+':'+c['source_path']],cwd=R)
 assert hashlib.sha256(original).hexdigest()==c['sha256']==hash_file(E/c['copy'])
b=R/'hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/processes/main-initial-route'
br=json.loads((b/'record.json').read_text())
assert hash_file(b/'stdout')==br['stdout_sha256'];assert hash_file(b/'stderr')==br['stderr_sha256']
# Every tracked change must belong to Issue 95; existing evidence is immutable.
changes=subprocess.check_output(['git','diff','--name-only','origin/main'],cwd=R,text=True).splitlines()
allowed=('docs/issue-95-freerouting-v250-run2.md','hardware/kicad/qualification/issue-95-freerouting-v250-run2/')
assert all(f==allowed[0] or f.startswith(allowed[1]) for f in changes),changes
s=json.loads((E/'summary.json').read_text())
assert s['baseline_v210']['completed_passes']==512 and s['baseline_v210']['maze_exception_events']==371
assert s['run1']['completed_passes']==18 and s['run1']['best_pass_unrouted']==58
assert json.loads((E/'command-comparison.json').read_text())['differences']==[
 {'index':15,'old':'--router.optimizer.enabled=false','new':'--router.optimizer.enabled=true'},
 {'index':16,'old':'--router.fanout.enabled=false','new':'--router.fanout.enabled=true'}]
for rel,expected in json.loads((E/'manifest.json').read_text()).items():
 assert hash_file(E/rel)==expected,rel
assert s['run2']['final_unrouted']==38 and s['run2']['optimizer_executed'] is False
print('PASS: hashes, raw reference provenance, recorded artifacts, command delta, baseline counts, and change scope')
