"""Audit saved results and seal submission hashes; never launch EDA tools."""
from pathlib import Path
import ast
import datetime
import hashlib
import json

E = Path(__file__).resolve().parent
R = E.parents[4]
T = R / '.issue131-runtime'
REPORT = R / 'docs/issue-131-wing-condition-search.md'


def load(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


verification = load(E / 'verification.json')
assert verification['pass_verification']
assessment = load(E / 'assessment.json')
expected = ['KRT-16-2L-0127', 'KRT-16-2L-0100', 'KRT-17-2L-0100']
assert verification['routing_order'] == expected
assert assessment['first_passing_16mm_cell'] == expected[1]
assert assessment['confirmation_cell'] == expected[2]
records = sorted((E / 'processes').glob('*/record.json'))
for path in records:
    record = load(path)
    assert record['exit_code'] == 0 and not record['timed_out'], path
assert len(list((E / 'processes').glob('stage0-equivalence'))) == 1
for cell, unconnected, tracks in zip(expected, [1, 0, 0], [855, 765, 727]):
    row = assessment['cells'][cell]
    inspection = E / 'inspection' / cell
    run = E / 'runs' / cell
    independent = load(inspection / 'assessment.json')
    assert set(row) - set(independent) == {'status', 'layers', 'width_mm'}
    assert all(row[key] == value for key, value in independent.items())
    assert row == load(run / 'report.json')['assessment']
    assert row['measured_unconnected'] == unconnected
    drc = load(inspection / 'drc.json')
    assert len(drc['unconnected_items']) == unconnected
    assert not drc['violations']
    width = load(inspection / 'width-audit.json')
    assert sum(width['track_width_histogram_mm'].values()) == tracks
    assert width['tracks_below_pinned'] == 0
    assert width['minimum_track_width_mm'] == row['width_mm']
    transfer = load(inspection / 'transfer-diff.json')
    assert not any(transfer.values())
    assert sha(run / 'out.kicad_pcb') == sha(inspection / 'main.kicad_pcb')
    if unconnected == 0:
        graph = load(inspection / 'copper-graph.json')
        assert not graph['shorts'] and not graph['disconnected']
    else:
        assert not (inspection / 'copper-graph.json').exists()
for cell in ['KRT-16-4L-0127', 'KRT-16-4L-0100']:
    assert assessment['cells'][cell]['status'] == 'NOT_RUN'
    for folder in ['runs', 'cell-inputs', 'inspection']:
        assert not (E / folder / cell).exists()
for name, record in load(E / 'harness-provenance.json').items():
    assert sha(E / name) == record['new_sha256']
    assert sha(R / record['source']) == record['source_sha256']

resume = load(T / 'submission-resume-hashes.json')
assert all(sha(R / name) == digest for name, digest in resume.items())
verification.update(
    submission_audit_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    saved_results_consistent_with_report=True,
    saved_process_records_checked=len(records),
    all_saved_processes_successful=True,
    route_gate_and_independent_inspection_reexecuted=False,
    original_evidence_files_preserved=len(resume),
    summary_inspection_and_run_reports_match=True,
    four_layer_inputs_and_runs_absent=True,
    manifest_algorithm='sha256',
    manifest_path_base='repository root',
    manifest_self_exclusion='manifest.json cannot hash itself; all other submission files are included',
)
paths = sorted(p for p in E.rglob('*') if p.is_file())
for path in paths:
    if path.suffix == '.json':
        load(path)
    if path.suffix == '.py':
        ast.parse(path.read_text())
verification['json_files_valid'] = sum(p.suffix == '.json' for p in paths)
verification['python_files_parse'] = sum(p.suffix == '.py' for p in paths)
save(E / 'verification.json', verification)
paths = [REPORT] + sorted(p for p in E.rglob('*') if p.is_file() and p.name != 'manifest.json')
save(E / 'manifest.json', {
    'algorithm': 'sha256',
    'path_base': 'repository root',
    'excluded': [str((E / 'manifest.json').relative_to(R))],
    'files': {str(p.relative_to(R)): sha(p) for p in paths},
})
print('Saved-result audit passed; sealed', len(paths), 'file hashes')
