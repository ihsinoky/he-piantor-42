"""Manifest all submitted bytes; report authored versus raw router whitespace."""
from common import *
import collections,ast
report=R/'docs/issue-141-wing-power-integrity.md';files=[report]+[p for p in E.rglob('*') if p.is_file() and p.name not in ['manifest.json','whitespace-audit.json']]
raw_whitespace=[];authored=[]
for p in files:
 if p.suffix in ['.py','.json','.md']:
  if p.suffix=='.py':ast.parse(p.read_text())
  elif p.suffix=='.json':json.loads(p.read_text())
  bad=[i for i,line in enumerate(p.read_text().splitlines(),1) if line.rstrip()!=line]
  if bad:authored.append(dict(path=str(p.relative_to(R)),lines=bad))
 elif p.suffix=='.kicad_pcb':
  bad=[i for i,line in enumerate(p.read_text().splitlines(),1) if line.rstrip()!=line]
  if bad:raw_whitespace.append(dict(path=str(p.relative_to(R)),lines=bad))
assert not authored,authored
save(E/'whitespace-audit.json',dict(authored_trailing_whitespace=authored,raw_pcb_whitespace=raw_whitespace,raw_preserved_byte_identically=True,utc=now()))
files.append(E/'whitespace-audit.json')
save(E/'manifest.json',{str(p.relative_to(R)):digest(p) for p in sorted(files)})
print('manifest',len(files),'files;',sum(p.stat().st_size for p in files),'bytes; raw PCB whitespace',sum(len(x['lines']) for x in raw_whitespace))
