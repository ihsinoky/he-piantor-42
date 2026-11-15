"""Find immutable round-3 operands by exact content hash in retained runtime CAD caches."""
import json,hashlib,shutil
from pathlib import Path
H=Path(__file__).resolve().parent;root=H.parents[2];runtime=root/'.issue248-runtime';scratch=runtime/'round6';scratch.mkdir(exist_ok=True)
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
want={r['sha256'] for pitch in (17,16) for r in read(H/f'round3/{pitch}mm/assembly-index.json') if not r['name'].startswith('Wire-') and r['name'] not in ('tray-left','tray-right','shell-central')}
folder=scratch/'frozen-operands';folder.mkdir(exist_ok=True)
found={}
for f in folder.glob('*.brep'):
 digest=sha(f)
 if digest in want:found[digest]=str(f.relative_to(root))
if set(found)!=want:
 for f in runtime.rglob('*.brep'):
  digest=sha(f)
  if digest in want and digest not in found:
   target=folder/(digest+'.brep');shutil.copyfile(f,target);found[digest]=str(target.relative_to(root))
assert set(found)==want,('Missing retained frozen BRep operands',sorted(want-set(found)))
(scratch/'frozen-operands.json').write_text(json.dumps(found,indent=2)+'\n')
print('Frozen BRep content recovery PASS',len(found),'unique operands')
