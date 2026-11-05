#!/usr/bin/env python3
"""Audit inputs, inventories, reference hashes, model sanity and additions only."""
import ast
import datetime as dt
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


baseline = json.loads((ROOT / '.issue138-runtime/baseline-hashes.json').read_text())
changed = [p for p, digest in baseline.items() if not (ROOT / p).is_file() or sha(ROOT / p) != digest]
assert not changed, changed
for p in OUT.glob('*.py'):
    ast.parse(p.read_text())
for p in OUT.rglob('*.json'):
    json.loads(p.read_text())
prov = json.loads((OUT / 'board-read-provenance.json').read_text())
for p in prov['sources']:
    assert sha(ROOT / p['path']) == p['sha256']
widths = json.loads((OUT / 'net-widths.json').read_text())
geometry = json.loads((OUT / 'geometry-and-board-evidence.json').read_text())
for g in geometry:
    cell = g['cell']
    inv = json.loads((OUT / (cell + '-inventory.json')).read_text())
    old = json.loads((ROOT / f'hardware/kicad/qualification/issue-131-wing-condition-search/evidence/inspection/{cell}/snapshot.json').read_text())
    assert len(inv['tracks']) == g['track_count']
    assert len(inv['vias']) == g['via_count']
    oldtracks = {t['uuid']: t for t in old['tracks'] if t['kind'] == 'track'}
    for t in inv['tracks']:
        a = oldtracks[t['uuid']]
        assert a['width'] == t['width_mm']
        assert a['start'] == t['start'] and a['end'] == t['end'] and a['net'] == t['net']
    assert sum(w['segments'] for w in widths if w['cell'] == cell) == g['track_count']
    assert sum(w['vias'] for w in widths if w['cell'] == cell) == g['via_count']
    assert len(g['npth']) == 4 and not g['slotted_drills'] and g['internal_edge_cuts'] == 0
    assert all(q['drill'] == [2.2, 2.2] for q in g['npth'])
    assert g['copper_layers'] == 2 and g['thickness_mm'] == 1.2
    assert g['all_zones_are_keepout_rule_areas']
for rec in json.loads((OUT / 'sources/reference-retrieval-records.json').read_text()):
    path = OUT / 'sources' / (rec['id'] + '.pdf')
    if path.exists():
        assert sha(path) == rec['sha256']
        assert path.read_bytes().startswith(b'%PDF')
assert all(c['external_edges_equal'] and c['npth_count_equal'] for c in json.loads((OUT / 'starting-evidence-comparison.json').read_text())['comparison'])
electrical = json.loads((OUT / 'electrical-evaluation.json').read_text())
assert len(electrical['net_checks']) == 60 and all(n['below_10K_screen'] for n in electrical['net_checks'])
assert abs(electrical['scenarios'][1]['supply_A'] - 0.1050081) < 1e-12

# An analytical circuit, independent of the board's topology, checks units,
# KCL, branch loads, and ground/source treatment in the supplementary model.
spec = importlib.util.spec_from_file_location('dc', OUT / 'estimate-dc-drop.py')
dc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dc)


def pad(ref, x):
    return dict(ref=ref, number='1', uuid=ref, net='HALL_5V', position=[x, 0],
                size=[1, 1], shape='rect', angle=0, layers=['F.Cu'])


def track(a, b):
    return dict(start=[a, 0], end=[b, 0], net='HALL_5V', width_mm=0.1, layer='F.Cu')


inv = dict(tracks=[track(0, 100)], pads=[pad('J_WING', 0), pad('U_H0', 100)], vias=[])
series = dc.model(inv, 'HALL_5V', 0.005, 0, 0.08, 20)
expected = 0.005 * 1.7241e-8 * 0.1 / (0.08 * 0.035 * 1e-6)
assert abs(series['pins']['U_H0.1'] - expected) < 1e-7
inv = dict(tracks=[track(0, 50), track(50, 100)],
           pads=[pad('J_WING', 0), pad('U_H0', 50), pad('U_H1', 100)], vias=[])
branch = dc.model(inv, 'HALL_5V', 0.005, 0, 0.08, 20)
half_r = 1.7241e-8 * 0.05 / (0.08 * 0.035 * 1e-6)
assert abs(branch['pins']['U_H0.1'] - 0.010 * half_r) < 1e-7
assert abs(branch['pins']['U_H1.1'] - 0.015 * half_r) < 1e-7
dc_results = json.loads((OUT / 'dc-drop-estimate.json').read_text())['results']
assert len(dc_results) == 10
assert all(r['supply']['kcl_residual_A'] < 1e-7 and r['ground']['kcl_residual_A'] < 1e-7 for r in dc_results)
gitdir = ROOT / '.issue138-runtime/git'
diff = subprocess.check_output(['git', '--git-dir=' + str(gitdir), '--work-tree=' + str(ROOT),
                                'diff', '--name-status', 'main'], text=True)
assert all(line.startswith('A\t') for line in diff.splitlines()), diff
record = dict(utc=dt.datetime.now(dt.timezone.utc).isoformat(), pass_audit=True,
              preserved_baseline_files=len(baseline), baseline_changes=changed,
              issue137_report_and_evidence_preserved=True, board_native_ast_and_saved_snapshot_agree=True,
              all_60_net_checks_pass_thermal_screen=True, source_hashes_verified=True,
              python_syntax_and_json_valid=True,
              dc_model_series_and_branched_analytic_cases_pass=True,
              dc_model_board_kcl_pass=True, staged_or_committed_diff_additions_only=True,
              limitations='Model sanity tests do not validate manufactured copper, thermal environment or analog accuracy')
(OUT / 'verification.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record, indent=2))
