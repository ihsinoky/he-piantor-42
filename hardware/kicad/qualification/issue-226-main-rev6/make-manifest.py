"""Hash final evidence and read-only inherited inputs; verification output excluded."""
from pathlib import Path
import hashlib,json,subprocess
E=Path(__file__).resolve().parent;R=E.parents[3];V=E.parent/'issue-221-main-rev5'
def row(p):return dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
files=[row(p) for p in sorted(E.rglob('*')) if p.is_file() and p.name not in ['manifest.json','verification.json'] and '__pycache__' not in p.parts]
files += [row(R/p) for p in ['docs/decisions.md','docs/findings.md','.issue226-runtime/REPORT.md']]
inputs=[V/'manifest.json',V/'inspection/final/main.kicad_pcb',V/'inspection/final/main.kicad_pro',V/'inspection/final/snapshot.json',V/'power-extraction-final.json',V/'ground-extraction-final.json',V/'resistance-summary.json',V/'power-budget.json',V/'manufacturing/BOM.csv',V/'manufacturing/CPL.csv',E.parent/'issue-185-main-rev3/main-bom.csv',E.parent/'issue-141-wing-power-integrity/dc-model.py',E.parent/'issue-141-wing-power-integrity/dc-drop-estimate.json',E.parent/'issue-87-native-main-routing/check-main.py',E.parent/'eda-004g/resume-02/read-pcb.py',E.parent/'issue-196-main-rev4-phasea2/geometry-plan.json',E.parent/'issue-175-main-dual-wing-final2/inputs/final/main.kicad_pro']
inputs+=sorted((V/'schematic').glob('*'));inputs+=sorted((V/'Rev5.pretty').glob('*'));inputs+=sorted((E.parent/'issue-196-main-rev4-phaseb/Rev4.pretty').glob('*'))
for name in ['connectivity.py','audit-vias.py','extract-power.py','extract-ground.py','summarize-resistance.py','power-budget.py','verify-ground-model.py','gerber-frame-cpl.py','check-cam.py']:inputs.append(V/name)
git=['git','--git-dir='+str(R/'.issue226-runtime/git'),'--work-tree='+str(R)]
base=subprocess.check_output(git+['rev-parse','HEAD'],text=True).strip() if not (E/'manifest.json').exists() else json.loads((E/'manifest.json').read_text())['base_commit']
(E/'manifest.json').write_text(json.dumps(dict(base_commit=base,files=files,inputs=[row(p) for p in sorted(set(inputs)) if p.is_file()]),indent=2)+'\n')
print('Manifest',len(files),'outputs',len(set(inputs)),'inputs')
