"""Bind saved artifacts and immutable baseline inputs after regeneration."""
from pathlib import Path
import json,hashlib,subprocess,os
E=Path(__file__).resolve().parent;ROOT=E.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Case source manifest includes study pad maps and all original STEP/dimension inputs.
inputs=json.loads((E/'case/inputs-sha256.json').read_text())
for path in [ROOT/'docs/decisions.md',E.parent/'issue-233-wing-single-sided/REPORT.md',E.parent/'issue-233-wing-single-sided/case/summary.json',ROOT/'hardware/jitx/wing/definition.py',*sorted((E.parent/'issue-233-wing-single-sided').glob('wing-*/blocking-regions.json'))]:inputs[str(path.relative_to(ROOT))]=sha(path)
main=json.loads((E/'main-unchanged.json').read_text());inputs[main['path']]=main['sha256']
# Hash every tracked input outside this study: catches any production-tree edit,
# removal or mutation to the immutable round-1 and Rev.3 references.
env={**os.environ,'GIT_DIR':str(ROOT/'.issue235-runtime/git'),'GIT_WORK_TREE':str(ROOT)}
changed=subprocess.check_output(['git','diff','--name-only','HEAD'],env=env,text=True).splitlines()
assert all(name.startswith(str(E.relative_to(ROOT))+'/') for name in changed),('baseline edits',changed)
files=subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD'],env=env,text=True).splitlines()
for name in files:
 if name.startswith(str(E.relative_to(ROOT))+'/') or name.startswith('.issue235-runtime/'):continue
 p=ROOT/name
 if p.is_file():inputs[name]=sha(p)
artifacts={str(p.relative_to(E)):sha(p) for p in sorted(E.rglob('*')) if p.is_file() and p.name not in ('evidence-manifest.json','verification.json') and '__pycache__' not in p.parts and p.suffix!='.kicad_prl'}
(E/'evidence-manifest.json').write_text(json.dumps({'schema':1,'artifact_sha256':artifacts,'input_sha256':inputs},indent=2)+'\n')
print('Bound',len(artifacts),'artifacts and',len(inputs),'input files')
