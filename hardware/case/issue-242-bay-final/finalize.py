"""Bind immutable inputs and completed audit files; no geometry or baseline edits."""
from pathlib import Path
import json,hashlib,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def main():
 for pitch in (16,17):
  src=ROOT/f'.issue242-runtime/audit{pitch}/index.json';out=HERE/f'{pitch}mm';a=json.loads((out/'audit.json').read_text());assert a['geometry_index_sha256']==sha(src)
  shutil.copyfile(src,out/'assembly-index.json')
 inputs=[HERE.parent/'issue-240-bay-cover/REPORT.md',HERE.parent/'issue-238-bay-study/REPORT.md',HERE.parent/'issue-232-final/REPORT.md',ROOT/'hardware/kicad/qualification/issue-240-main-rev7/REPORT.md',ROOT/'hardware/kicad/qualification/issue-240-main-rev7/inspection/final/main.kicad_pcb',ROOT/'hardware/kicad/qualification/issue-240-main-rev7/invariants.json',HERE.parent/'issue-238-bay-study/main-inventory.json',ROOT/'hardware/kicad/qualification/issue-235-wing-round2/main-native-obstacles.json',ROOT/'docs/decisions.md']
 for pitch in (16,17):
  inputs += [HERE.parent/f'issue-232-final/{pitch}mm/assembly.step',HERE.parent/f'issue-232-final/{pitch}mm/inputs-sha256.json',HERE.parent/f'issue-228-final/{pitch}mm/dimensions.json',HERE.parent/f'issue-238-bay-study/{pitch}mm-measurements.json']
  for rel in json.loads((HERE.parent/f'issue-232-final/{pitch}mm/inputs-sha256.json').read_text()):
   path=ROOT/rel
   if path.exists():inputs.append(path)
 save(HERE/'inputs-sha256.json',{str(p.relative_to(ROOT)):sha(p) for p in set(inputs)})
 save(HERE/'artifact-sha256.json',{str(p.relative_to(HERE)):sha(p) for p in HERE.rglob('*') if p.is_file() and p.name!='artifact-sha256.json'})
if __name__=='__main__':main()
