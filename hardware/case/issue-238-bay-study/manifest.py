"""Bind deliverable bytes. --write updates only this study's manifest."""
import sys,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
actual={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(P.rglob('*')) if p.is_file() and p.name!='artifact-sha256.json' and '__pycache__' not in p.parts}
if '--write' in sys.argv:(P/'artifact-sha256.json').write_text(json.dumps(actual,indent=2)+'\n')
else:assert actual==json.loads((P/'artifact-sha256.json').read_text()),'Deliverable byte mismatch'
print(f'Artifact manifest: {len(actual)} files verified')
