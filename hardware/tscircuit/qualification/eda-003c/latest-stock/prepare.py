"""Copy unchanged EDA-003B fixture/verifiers beneath isolated dependency root."""
from pathlib import Path
import hashlib
import json

here = Path(__file__).resolve().parent
production = here.parents[2]
assert json.loads((production/'package.json').read_text())['dependencies']['tscircuit'] == '0.0.2646'
assert json.loads((here/'package.json').read_text())['dependencies']['tscircuit'] == '0.0.2748'
files = [
    'src/qualification/revm1-routing-proof.tsx',
    'src/qualification/JstGh14.tsx',
    'src/qualification/native-support-footprints.tsx',
    'src/components/HallKey.tsx',
    'scripts/generate-revm1-routing-proof.tsx',
    'scripts/revm1-physical-connectivity.ts',
    'scripts/verify-revm1-routing-proof.ts',
    'scripts/test-revm1-physical-connectivity.ts',
    'scripts/verify-revm1-scope.ts',
    'scripts/verify-revm1-manufacturing.py',
    'scripts/verify-revm1-reproducibility.py',
]
records = []
for name in files:
    raw = (production/name).read_bytes()
    copied = raw
    if name == 'scripts/generate-revm1-routing-proof.tsx':
        copied = raw.replace(b'0.0.2646', b'0.0.2748').replace(b'production 0.0.2748 pin', b'isolated 0.0.2748 pin')
    target = here/name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(copied)
    records.append({'file': name, 'original_sha256': hashlib.sha256(raw).hexdigest(),
                    'experiment_sha256': hashlib.sha256(copied).hexdigest(),
                    'adaptation': 'mechanical environment pin guard only' if copied != raw else 'none'})
(here.parent/'evidence/source-comparability.json').write_text(json.dumps({
    'strategy': 3, 'behavior_affecting_design_changes': [], 'files': records,
    'isolation': 'Copies resolve imports beneath latest-stock/node_modules; original sources untouched.'
}, indent=2)+'\n')
print('Fixture and verifier copies prepared; no design/API changes.')
