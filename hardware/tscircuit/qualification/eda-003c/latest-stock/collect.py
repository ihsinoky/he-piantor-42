"""Retain compact Stage 1 evidence from an inspected two-run screening directory.
Usage: python3 collect.py OUTPUT_ROOT
"""
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import sys

here = Path(__file__).resolve().parent
root = Path(sys.argv[1]).resolve()
evidence = here.parent/'evidence'
rawdir = evidence/'raw'
rawdir.mkdir(exist_ok=True)
exits = json.loads((root/'run-exits.json').read_text())


def write(name, value):
    (evidence/name).write_text(json.dumps(value, indent=2)+'\n')


def metrics(summary):
    counts = summary['stock_check_counts']
    diagnostics = summary['stock_material_diagnostics']
    return {
        'electrically_required_unrouted_count': summary['electrically_required_unrouted_count'],
        'wrong_net_copper_components': summary['wrong_net_copper_components'],
        'wrong_net_copper_component_count': len(summary['wrong_net_copper_components']),
        'trace_count': summary['routed_trace_count'], 'via_count': summary['via_count'],
        'pad_pad_errors': counts.get('pcb_pad_pad_clearance_error', 0),
        'pad_trace_errors': counts.get('pcb_pad_trace_clearance_error', 0),
        'via_trace_errors': counts.get('pcb_via_trace_clearance_error', 0),
        'trace_errors': counts.get('pcb_trace_error', 0),
        'autorouter_errors': summary['generated_diagnostic_counts'].get('pcb_autorouting_error', 0),
        'placement_routing_created_errors': counts.get('pcb_placement_error', 0),
        'keepout_via_errors': sum('keepout' in d['message'] for d in diagnostics),
        'hole_trace_errors': sum(d['type'] == 'pcb_trace_error' and 'pcb_hole' in d['message'] for d in diagnostics),
        'result': summary['result'],
    }


comparison = {'baseline_aggregate': '0.0.2646', 'latest_aggregate': '0.0.2748', 'strategy': 3, 'boards': {}}
artifacts = {}
for board in ('main', 'wing'):
    baseline = json.loads((here.parents[1]/'eda-003b/evidence'/f'final-{board}-summary.json').read_text())
    latest = json.loads((root/f'{board}-1/summary.json').read_text())
    generation = json.loads((root/f'{board}-1/generation.json').read_text())
    latest['generation'] = generation
    latest['router_settled'] = any(e['event'] == 'autorouting:end' for e in generation['events']) and not generation['timed_out']
    latest['screening_metrics'] = metrics(latest)
    write(f'latest-{board}-summary.json', latest)
    repeat = json.loads((root/f'{board}-2/summary.json').read_text())
    repeat['generation'] = json.loads((root/f'{board}-2/generation.json').read_text())
    write(f'latest-{board}-run2-summary.json', repeat)
    comparison['boards'][board] = {'baseline': metrics(baseline), 'latest': metrics(latest)}
    for name in ('circuit.json', 'manufacturing.zip'):
        data = (root/f'{board}-1'/name).read_bytes()
        filename = f'latest-{board}.{name}.gz'
        (rawdir/filename).write_bytes(gzip.compress(data, mtime=0))
        artifacts[filename] = {'uncompressed_sha256': hashlib.sha256(data).hexdigest(), 'uncompressed_bytes': len(data)}
    for repeat in (1, 2):
        src = root/f'{board}-{repeat}/manufacturing-summary.json'
        if src.exists():
            shutil.copyfile(src, evidence/f'{board}-run{repeat}-manufacturing.json')
        else:
            label = f'manufacturing-{board}-{repeat}'
            assert exits[label] != 0, 'Missing successful manufacturing summary'
            write(f'{board}-run{repeat}-manufacturing.json', {
                'result': 'FAIL', 'export_command_exit_code': exits[f'export-{board}-{repeat}'],
                'verifier_exit_code': exits[label],
                'verifier_output': (root/(label+'.log')).read_text(),
                'scope': 'Existing segment-survival assertion; later checks not completed; no geometry-loss root cause inferred.'
            })
    shutil.copyfile(root/f'{board}-reproducibility.json', evidence/f'{board}-reproducibility.json')
write('baseline-comparison.json', comparison)
write('raw/artifact-manifest.json', artifacts)
