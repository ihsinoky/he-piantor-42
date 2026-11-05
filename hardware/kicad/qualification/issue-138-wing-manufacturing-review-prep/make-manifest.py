#!/usr/bin/env python3
"""Hash the report and all submitted evidence except the manifest itself."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
files = [ROOT / 'docs/issue-138-wing-manufacturing-review-prep.md']
files += sorted(p for p in OUT.rglob('*') if p.is_file() and p.name != 'manifest.json')
manifest = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(f'{len(files)} files hashed (manifest itself excluded)')
