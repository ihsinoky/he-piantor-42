"""Hash final outputs plus fixed Rev4/PR220 inputs; verification is derived."""
from pathlib import Path
import hashlib,json
E=Path(__file__).resolve().parent;R=E.parents[3];V=E.parent/'issue-196-main-rev4-phaseb'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[p for p in E.rglob('*') if p.is_file() and p.suffix!='.kicad_prl' and p.name not in ['manifest.json','verification.json']]
assert not any('__pycache__' in p.parts for p in files),'Do not commit runtime bytecode'
files += [R/'.issue221-runtime/REPORT.md',R/'docs/issue-221-main-rev5.md',R/'docs/decisions.md',R/'docs/project-status.md']
inputs=[V/p for p in ['inspection/final/main.kicad_pcb','inspection/final/main.kicad_pro','inspection/final/snapshot.json','schematic/main.kicad_sch','schematic/main.net.xml','manufacturing/BOM.csv','manufacturing/CPL.csv','resistance-summary.json','power-budget.json']]
inputs +=[E.parent/'issue-219-cpl-frame/verification.json']
(E/'manifest.json').write_text(json.dumps(dict(base_commit='227eb17a',files=[dict(path=str(p.relative_to(R)),sha256=sha(p)) for p in sorted(files)],inputs=[dict(path=str(p.relative_to(R)),sha256=sha(p)) for p in sorted(inputs)]),indent=2)+'\n')
print('Manifest:',len(files),'outputs;',len(inputs),'fixed inputs')
