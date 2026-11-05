"""Read-only local evidence verification. Run from repository root."""
from pathlib import Path
import csv
import hashlib
import json
import re
import subprocess
import sys

R = Path(__file__).resolve().parents[3]
E = Path(__file__).resolve().parent
report = R / 'docs/issue-150-case-stage1.md'
expected = (E / 'measurements.json').read_bytes()
r = subprocess.run([sys.executable, str(E / 'measure.py')], cwd=R, capture_output=True, check=True)
assert r.stdout == expected, 'non-reproducible measurements'
m = json.loads(expected)
for p,v in m['wings'].items():
    with (E / f'keys-{p}mm.csv').open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == len(v['keys']) == 21
    for row,k in zip(rows,v['keys']):
        assert row['key'] == k['key'] and row['sensor'] == k['ref']
        assert float(row['kicad_x_mm']) == k['x'] and float(row['kicad_y_mm']) == k['y']
    assert v['fit']['switch_conservative']['overlap_pairs'] == []
    assert v['fit']['custom_cap_max']['overlap_pairs'] == []
    assert len(v['fit']['dsa_nominal']['overlap_pairs']) == (50 if p == '16' else 41)
    # Verify original #149 CSVs, allowing for their column names.
    with (E / f'inputs/issue149-mounting-{p}mm.csv').open() as f:
        holes = list(csv.DictReader(f))
    assert len(holes) == 4
    actual = sorted((float(h['x_mm']),float(h['y_mm']),float(h['diameter_mm'])) for h in holes)
    native = sorted((h['x'],h['y'],float(h['drill'][0])) for h in v['native']['holes'])
    assert actual == native
    assert all(float(h['keepout_diameter_mm']) == 5.0 for h in holes)
json_count = 0
for path in E.rglob('*.json'):
    json.loads(path.read_text())
    json_count += 1
links = 0
for path in [report, E/'README.md']:
    for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
        if target.startswith(('https:', 'http:', '#')):
            continue
        dest = target.split('#')[0]
        assert (path.parent / dest).exists(), (path, dest)
        links += 1
local_silk_checks = 0
for p,v in json.loads((E/'inputs/issue149-interface.json').read_text()).items():
    path = R / v['path']
    if path.exists():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == v['sha256']
        local_silk_checks += 1
manifest_path = E/'manifest.json'
if manifest_path.exists():
    manifest = json.loads(manifest_path.read_text())
    for path,digest in manifest['files'].items():
        assert hashlib.sha256((R/path).read_bytes()).hexdigest() == digest, path
baseline = R/'.issue150-runtime/protected-files.json'
protected = None
if baseline.exists():
    files = json.loads(baseline.read_text())
    for path,digest in files.items():
        assert hashlib.sha256((R/path).read_bytes()).hexdigest() == digest, path
    protected = len(files)
print(json.dumps(dict(pass_verification=True,deterministic_measurements=True,
    keys_per_pitch=21,pairs_per_pitch=210,json_files=json_count,local_links=links,
    local_issue149_pcb_hashes_checked=local_silk_checks,protected_existing_files=protected,
    physical_tests='not performed',cad_changes='none'),indent=2))
