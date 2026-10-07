"""Validate complete record coverage, geometric merge proofs and file integrity."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import classify

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
E = HERE/'evidence'
BASE = '820e7d7a99aa8c078f88ce3d0602b7ff4f4399f8'


def hashes():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in E.iterdir()
            if p.name in ('error-records-normalized.json', 'physical-fault-clusters.json')}


# A larger search budget may choose different equally valid merge witnesses.
# Compare physical component membership/geometry separately from those choices.
classify.MAX_FEASIBILITY_ITERATIONS = 800
with contextlib.redirect_stdout(io.StringIO()):
    classify.classify()
lower_r = (E/'error-records-normalized.json').read_bytes()
lower_c = json.loads((E/'physical-fault-clusters.json').read_text())
classify.MAX_FEASIBILITY_ITERATIONS = 4000
with contextlib.redirect_stdout(io.StringIO()):
    classify.classify()
higher_c = json.loads((E/'physical-fault-clusters.json').read_text())
assert lower_r == (E/'error-records-normalized.json').read_bytes()
assert lower_c['clusters'] == higher_c['clusters'], 'Faults changed at increased numeric budget'
# Restore the normal budget and verify exact byte determinism, including proofs.
classify.MAX_FEASIBILITY_ITERATIONS = 800
with contextlib.redirect_stdout(io.StringIO()):
    classify.classify()
before = hashes()
with contextlib.redirect_stdout(io.StringIO()):
    classify.classify()
assert before == hashes(), 'Repeated classification is not deterministic'
r = json.loads((E/'error-records-normalized.json').read_text())
c = json.loads((E/'physical-fault-clusters.json').read_text())
assert len(r) == 71 and len(c['clusters']) == 54
assert set(e['record_id'] for e in r) == set(i for x in c['clusters'] for i in x['record_ids'])
assert len({tuple(x['nets']) for x in c['clusters']}) == 37
primitives = [p for record in r for p in record['violating_primitive_pairs']]
required = {e['record_id']: e['required_clearance_mm'] for e in r}
event_records = [record['record_id'] for record in r for _ in record['violating_primitive_pairs']]
for proof in c['merge_proofs']:
    p, q = proof['points']
    for i in proof['event_indices']:
        shapes = primitives[i]['geometry']
        assert classify.contains(shapes[0], p) and classify.contains(shapes[1], q), proof
        assert classify.norm(classify.sub(p, q)) < required[event_records[i]], proof
assert len(c['merge_proofs']) == len(primitives)-len(c['clusters'])
subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(HERE), '-p', 'test_classifier.py'], check=True)
subprocess.run(['node', str(HERE/'capture-checks.mjs')], check=True)
subprocess.run([sys.executable, str(HERE/'summarize.py')], check=True)
protected = ['hardware/tscircuit/package.json', 'hardware/tscircuit/package-lock.json',
             'hardware/tscircuit/qualification/eda-003b', 'hardware/tscircuit/qualification/eda-003c']
files = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE, '--', *protected], cwd=ROOT, text=True).splitlines()
for path in files:
    baseline = subprocess.check_output(['git', 'show', BASE+':'+path], cwd=ROOT)
    assert (ROOT/path).read_bytes() == baseline, 'Protected file changed: '+path
assert json.loads((ROOT/'hardware/tscircuit/package.json').read_text())['dependencies']['tscircuit'] == '0.0.2646'
assert json.loads((ROOT/'hardware/tscircuit/package-lock.json').read_text())['packages']['node_modules/tscircuit']['version'] == '0.0.2646'
json_files = list(E.glob('*.json'))
for p in json_files:
    json.loads(p.read_text())
ET.parse(E/'main-fault-map.svg')
subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
result = dict(json_parse='PASS', svg_parse='PASS', all_71_record_coverage='PASS',
    geometry_primitive_pair_count=len(primitives), merge_witness_proofs_checked=len(c['merge_proofs']),
    deterministic_clustering='PASS: exact repeat bytes at 800; identical component membership/geometry and normalized records at 800 and 4000; merge witness choices can differ',
    classifier_fault_unit_checks=14, stock_check_replay='PASS: matches all accepted 71 type/message records',
    protected_tracked_files_checked=len(files), production_manifest_lock='byte-identical to baseline',
    production_tscircuit='0.0.2646', accepted_eda_003c='byte-identical to baseline', historical_eda_003b='byte-identical to baseline',
    git_diff_check='PASS', router_runs=0, clearance_acceptance='FAIL (accepted material errors persist)')
(E/'validation.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result))
