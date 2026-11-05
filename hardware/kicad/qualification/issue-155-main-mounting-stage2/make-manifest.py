"""Hash committed evidence candidates and their two permitted document changes."""
from common import *
paths=[p for p in E.rglob('*') if p.is_file() and p.name!='manifest.json' and '__pycache__' not in p.parts and p.suffix not in ['.pyc','.kicad_prl']]
save(E/'manifest.json',dict(utc=now(),files={str(p.relative_to(E)):digest(p) for p in sorted(paths)},documents={str(p.relative_to(R)):digest(p) for p in [R/'docs/decisions.md',R/'docs/issue-155-main-mounting-stage2.md']},exclusions=['manifest.json itself','__pycache__','*.pyc','*.kicad_prl','all runtime directories']))
print('Manifest:',len(paths),'evidence files and two documents')
