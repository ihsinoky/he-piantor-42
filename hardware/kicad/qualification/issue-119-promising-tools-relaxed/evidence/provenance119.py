from pathlib import Path
import subprocess,json,hashlib,shutil
R=Path.cwd();E=R/'hardware/kicad/qualification/issue-119-promising-tools-relaxed/evidence';git=['git','--git-dir=/tmp/issue-119-main/git'];ref=json.loads((E/'start.json').read_text())['source117_commit'];prefix='hardware/kicad/qualification/issue-117-four-layer-main/evidence/'
for rel in ['amendment-01/assessment.json','amendment-01/verification.json','amendment-01/smoke-gate.json','amendment-01/equivalence-gate-02.json']+[f'amendment-01/inspection/main/{r}/{f}' for r in ['fab','krt'] for f in ['drc.json','independent.json','unconnected-net-endpoints.json']]:
 p=E/'source-117'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(subprocess.check_output(git+['show',ref+':'+prefix+rel]))
p=E/'source-117/report.md';p.write_bytes(subprocess.check_output(git+['show',ref+':docs/issue-117-four-layer-main-and-wing-outlook.md']))
files={str(p.relative_to(E/'source-117')):hashlib.sha256(p.read_bytes()).hexdigest() for p in (E/'source-117').rglob('*') if p.is_file()}
(E/'source-117-provenance.json').write_text(json.dumps(dict(commit=ref,branch='origin/issue-117-four-layer-main',method='git show branch commit:path; no source read from main or local untracked copies',files=files),indent=2)+'\n')
for name in ['setup119.py','provenance119.py']:
 shutil.copy('/tmp/'+name,E/name)
# Save local fixed two-layer input verification against committed historical branch.
rows={}
for stage in ['main','smoke']:
 for name in ['main.kicad_pcb','main.kicad_pro','corrected.dsn']:
  rel=f'hardware/kicad/qualification/issue-115-kicad-routing-tools-escalation-off/evidence/inputs/{stage}/{name}'
  blob=subprocess.check_output(git+['show','origin/issue-115-kicad-routing-tools-escalation-off:'+rel]);actual=(R/rel).read_bytes();assert blob==actual
  rows[rel]=hashlib.sha256(blob).hexdigest()
(E/'source-115-provenance.json').write_text(json.dumps(dict(commit=subprocess.check_output(git+['rev-parse','origin/issue-115-kicad-routing-tools-escalation-off'],text=True).strip(),local_copy_byte_identical_to_branch_blob=True,files=rows),indent=2)+'\n')
