"""Reproduce Stage 1 in fresh processes; does not infer a terminal classification.

Usage: BUN=... python3 screen.py /tmp/UNUSED_OUTPUT_ROOT
Run npm ci --ignore-scripts first, from this isolated directory.
"""
import json
import os
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
out = Path(sys.argv[1]).resolve()
assert not out.exists(), 'Use a newly absent output directory'
out.mkdir(parents=True)
bun = os.environ.get('BUN', 'bun')
exits = {}
subprocess.run([sys.executable, str(here/'prepare.py')], check=True)


def run(args, label, expected=(0,)):
    with (out/(label+'.log')).open('w') as log:
        result = subprocess.run(args, cwd=here, stdout=log, stderr=subprocess.STDOUT)
    exits[label] = result.returncode
    (out/'run-exits.json').write_text(json.dumps(exits, indent=2)+'\n')
    assert result.returncode in expected, f'{label}: exit {result.returncode}; see log'


run([bun, 'scripts/test-revm1-physical-connectivity.ts'], 'verifier-fault-fixtures')
for repeat in (1, 2):
    for board in ('main', 'wing'):
        directory = out/f'{board}-{repeat}'
        run([bun, 'scripts/generate-revm1-routing-proof.tsx', board, '3', str(directory)], f'generate-{board}-{repeat}')
        run([bun, 'scripts/verify-revm1-routing-proof.ts', str(directory/'circuit.json'), str(directory/'summary.json')], f'verify-{board}-{repeat}', (0, 1))
        assert (directory/'summary.json').exists(), 'Verifier did not produce evidence'
        generation = json.loads((directory/'generation.json').read_text())
        assert not generation['timed_out'], 'Bounded routing timed out'
        assert any(e['event'] == 'autorouting:end' for e in generation['events']), 'Router did not complete'
        run([bun, 'node_modules/@tscircuit/cli/dist/cli/main.js', 'export', str(directory/'circuit.json'), '--format', 'gerbers', '--output', str(directory/'manufacturing.zip')], f'export-{board}-{repeat}')
        run([sys.executable, 'scripts/verify-revm1-manufacturing.py', str(directory/'circuit.json'), str(directory/'manufacturing.zip'), str(directory/'manufacturing-summary.json')], f'manufacturing-{board}-{repeat}', (0, 1))
for board in ('main', 'wing'):
    run([sys.executable, 'scripts/verify-revm1-reproducibility.py', str(out/f'{board}-1'), str(out/f'{board}-2'), str(out/f'{board}-reproducibility.json')], f'reproducibility-{board}', (0, 1))
run([bun, 'scripts/verify-revm1-scope.ts', str(out/'main-1/circuit.json'), str(out/'wing-1/circuit.json'), str(out/'scope.json')], 'scope')
print(f'Screening output: {out}; inspect summaries before making a decision.')
