#!/usr/bin/env python3
"""Check evidence integrity. A pass is NOT a PCB or USB qualification pass."""
from pathlib import Path
import csv
import gzip
import hashlib
import json
import re

E = Path(__file__).resolve().parent
R = E.parents[3]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(name):
    return json.loads((E/name).read_text())


decision = R/'docs/decisions.md'
raw = decision.read_bytes()
marker = b'\n## D-026 - '
assert raw.count(marker) == 1
prefix = raw.split(marker)[0]
imports = read('import-proof.json')
assert len(imports['files']) == 70
for item in imports['files']:
    actual = hashlib.sha256(prefix).hexdigest() if item['path'] == 'docs/decisions.md' else sha(R/item['path'])
    assert actual == item['sha256'], item['path']
assert b'mechanical policy **(b), design' in raw
assert b'not gates for Issue' in raw

protected = json.loads(gzip.decompress((E/'protected-start.json.gz').read_bytes()))
for path, digest in protected.items():
    actual = hashlib.sha256(prefix).hexdigest() if path == 'docs/decisions.md' else sha(R/path)
    # Full local worktree audit requires the historical untracked inputs too.
    assert actual == digest, path
for path, digest in read('input-hashes.json').items():
    assert sha(R/path) == digest, path

currents = list(csv.DictReader((E/'current-budget.csv').open()))
assert len(currents) == 30
for x in currents:
    load, rail, eta = map(float, [x['branch_A'],x['rail_V'],x['efficiency']])
    i = float(x['converter_input_at_4V75_A'])
    assert abs(i*4.75*eta-2*load*rail) < 1e-12
    assert abs(float(x['remaining_other_Main_at_USB_500mA_A'])+i-.5) < 1e-12
    assert abs(float(x['remaining_other_Main_at_USB_100mA_A'])+i-.1) < 1e-12

sweep = list(csv.DictReader((E/'upstream-sensitivity.csv').open()))
assert len(sweep) == 4320
for x in sweep:
    vin, source, current, other, up, pcb, branch, rail, eta = map(float,
        [x[k] for k in ['converter_input_V','source_V','USB_current_A','other_Main_A',
         'upstream_loop_ohm','pcb_loop_ohm','branch_A','rail_V','efficiency']])
    assert abs(vin+(up+pcb)*current-source) < 1e-12
    assert abs((current-other)*vin*eta-2*branch*rail) < 1e-12
    if source == 4.75 and up+pcb > 0:
        assert vin < 4.75 and x['input_4V75_met'] == 'False'

downstream = list(csv.DictReader((E/'conditional-downstream.csv').open()))
assert len(downstream) == 48
assert all('NOT extracted' in x['scope'] for x in downstream)
power = read('power-preflight.json')
assert power['sweep_rows'] == 4320 and power['previous_converter_rows_reproduced'] == 12
assert abs(power['counterexample']['converter_input_V']-4.682107148092307) < 1e-12
state = read('status.json')
assert state['route_attempts'] == 0
assert state['mechanical_physical_checks_are_gate'] is False
assert state['issue_complete'] is False
assert all(v is None for v in state['independent_metrics'].values())
native = read('native-readback.json')
assert native['PCB_sha256'] == 'fdc1a7748f94714e395eb50f3e08c43afa24192ee76eb3d1804a8cba28690222'
assert native['board_unchanged'] and not native['J3_present']

authored = [R/'docs/issue-167-main-dual-wing-stage2.md',E/'README.md',E/'draft-pr-body.md']
links = []
for p in authored:
    for target in re.findall(r'\]\(([^)]+)\)', p.read_text()):
        if '://' in target or target.startswith('#'):
            continue
        file = target.split('#')[0]
        assert (p.parent/file).exists(), (str(p), target)
        links.append(target)
    assert all(line.rstrip() == line for line in p.read_text().splitlines()), p

result = dict(status='pass',scope='evidence integrity only; issue incomplete and board qualification NOT performed',
    imported_paths_checked=70, D026_append_only=True, protected_files_checked=len(protected),
    input_hashes_checked=len(read('input-hashes.json')), arithmetic_upstream_rows=4320,
    current_rows=30, downstream_conditional_rows=48, previous_converter_rows_reproduced=12,
    authored_local_links_checked=len(links), starting_PCB_hash_unchanged=True,
    independent_metrics=state['independent_metrics'], route_attempts=0,
    CAM_generated=False, POFV_reclassified=False, PCBA_quote_updated=False)
(E/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
