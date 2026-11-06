#!/usr/bin/env python3
"""Reproduction, numerical invariants, source and worktree preservation checks."""
from pathlib import Path
import csv
import datetime
import gzip
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from urllib.parse import unquote

sys.dont_write_bytecode = True
E = Path(__file__).resolve().parent
R = E.parents[3]
T = R / '.issue165-runtime'
REPORT = R / 'docs/issue-165-dual-wing-power-study.md'
checks = {}


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def run(name, argv):
    out = E / 'processes' / name
    out.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1',
               TMPDIR=str(T), PYTHONPATH=str(R / '.issue141-runtime/geometry/lib/python3.12/site-packages'))
    for kind in ['CONFIG', 'CACHE', 'DATA', 'STATE']:
        d = T / kind.lower()
        d.mkdir(exist_ok=True)
        env['XDG_' + kind + '_HOME'] = str(d)
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    begin = time.monotonic()
    with (out / 'stdout').open('w') as stdout, (out / 'stderr').open('w') as stderr:
        p = subprocess.run(argv, cwd=R, env=env, stdout=stdout, stderr=stderr, timeout=180)
    save(out / 'record.json', dict(argv=argv, start_utc=start, exit_code=p.returncode,
                                 elapsed_s=time.monotonic()-begin, timeout_s=180,
                                 temp_directory=str(T), bytecode_writes=False))
    assert p.returncode == 0, (name, (out / 'stderr').read_text())


run('copper-study', [sys.executable, str(E / 'copper-study.py')])
run('comparison', [sys.executable, str(E / 'compare.py')])
checks['calculations_exited_zero'] = True
model = json.loads((E / 'model.json').read_text())
assert model['reproduced_157_rows'] == 768
assert model['max_reproduction_error_V'] < 1e-12
checks['reproduced_157_rows'] = 768
checks['max_reproduction_error_V'] = model['max_reproduction_error_V']

rows = list(csv.DictReader((E / 'sensitivity.csv').open()))
assert len(rows) == 14976
assert len({r['architecture'] for r in rows}) == 13
for p in rows:
    get = lambda k: float(p[k])
    total_loss = sum(get(k) for k in ['switch_drop_V', 'main_drop_V', 'harness_drop_V', 'wing_drop_V'])
    assert abs(get('sensor_voltage_V') - (get('source_floor_V')-total_loss)) < 1e-12
    assert abs(get('dc_margin_V') - (get('sensor_voltage_V')-get('operating_minimum_V'))) < 1e-12
    if p['load_case'] == 'envelope11mA':
        assert abs(get('branch_current_A') - .2310081) < 1e-12
    if p['load_case'] == 'allowance278mA':
        assert get('branch_current_A') == .278
checks['sensitivity_rows_and_unchanged_envelopes'] = len(rows)
primary = list(csv.DictReader((E / 'primary.csv').open()))
fixed = list(csv.DictReader((E / 'primary-fixed-pad-via.csv').open()))
assert len(primary) == 52 and len(fixed) == 96
for p in primary:
    assert p['pitch_mm'] == '17' and p['temperature_C'] == '125'
    assert float(p['width_factor']) == .8 and float(p['input_V']) == 4.75
    assert float(p['contact_each_ohm']) == .05 and p['return_conductors'] == '6'
    if 'target' not in p['architecture']:
        assert float(p['branch_current_A']) == .127
for p in fixed:
    assert .5 < float(p['wing_resistance_factor']) < .53
    assert abs(float(p['sensor_voltage_V']) - (float(p['source_floor_V']) - sum(float(p[k]) for k in
               ['switch_drop_V', 'main_drop_V', 'harness_drop_V', 'wing_drop_V']))) < 1e-12
checks['primary_rows'] = len(primary)
checks['fixed_pad_via_rows'] = len(fixed)

cp = json.loads((E / 'copper-study.json').read_text())
assert cp['original_function_modified'] is False and len(cp['results']) == 10
assert all(p['absolute_error_V'] < 1e-8 for p in cp['reproduction'])
assert all(len(p['sensors']) == 21 and p['max_kcl_residual_A'] < 1e-7 for p in cp['results'])
checks['copper_original_reproduced_and_all_21_points'] = True

# Source byte preservation, including unmerged decision/Issue inputs.
inputs = json.loads((E / 'input-hashes.json').read_text())
assert all(digest(R / p) == h for p, h in inputs.items())
checks['input_hashes'] = len(inputs)
snapshots = ['docs/decisions.md', 'docs/issue-163-main-dual-wing-plan-c.md',
             'hardware/kicad/qualification/issue-163-main-dual-wing-plan-c/ideal-main-dc.csv',
             'hardware/kicad/qualification/issue-163-main-dual-wing-plan-c/power-preflight.json']
assert all((E / 'inputs' / Path(p).name).read_bytes() == (R / p).read_bytes() for p in snapshots)
checks['byte_identical_input_snapshots'] = len(snapshots)

protected = E / 'protected-start.json.gz'
if not protected.exists():
    with gzip.open(protected, 'wb') as f:
        f.write((T / 'protected-start.json').read_bytes())
baseline = json.loads(gzip.decompress(protected.read_bytes()))
changed = [p for p, h in baseline.items() if not (R / p).is_file() or digest(R / p) != h]
assert not changed, changed
checks['preexisting_files_checked'] = len(baseline)
checks['preexisting_files_changed'] = changed

git = ['git', '--git-dir=' + str(T / 'git'), '--work-tree=' + str(R)]
start = json.loads((E / 'start.json').read_text())
base = start['base_commit']
assert subprocess.check_output(git + ['merge-base', 'HEAD', base], text=True).strip() == base
assert subprocess.check_output(git + ['branch', '--show-current'], text=True).strip() == start['branch']
allowed = lambda p: p == 'docs/issue-165-dual-wing-power-study.md' or p.startswith(str(E.relative_to(R)) + '/')
committed = subprocess.check_output(git + ['diff', '--name-status', base, 'HEAD'], text=True).splitlines()
staged = subprocess.check_output(git + ['diff', '--cached', '--name-status', base], text=True).splitlines()
for lines in [committed, staged]:
    assert all(line.startswith('A\t') and allowed(line.split('\t', 1)[1]) for line in lines), lines
worktree = subprocess.check_output(git + ['diff', '--name-only'], text=True).splitlines()
assert all(allowed(p) or p in start['preexisting_tracked_changes'] for p in worktree)
checks['base_commit'] = base
checks['branch'] = start['branch']
checks['committed_additions'] = len(committed)
checks['staged_additions'] = len(staged)
checks['preexisting_tracked_changes_not_staged'] = start['preexisting_tracked_changes']

# Check authored links; historical byte-preserved input links keep original paths.
bad_links = []
for path in [REPORT, E / 'README.md', E / 'draft-pr-body.md']:
    for href in re.findall(r'\]\(([^)]+)\)', path.read_text()):
        if re.match(r'[a-z]+://|#', href):
            continue
        target = unquote(href.split('#')[0])
        if target and not (path.parent / target).exists():
            bad_links.append([str(path.relative_to(R)), target])
assert not bad_links, bad_links
checks['authored_local_links_pass'] = True

# Ensure the report's values are formatted from computed primary/combined rows.
text = REPORT.read_text()
for p in primary + fixed:
    if p['main_common_ohm'] not in ['0.0', '0.25'] or p['return_conductors'] != '6' or p['load_case'] != 'planning127mA':
        continue
    if p['architecture'] in ['copper_half', 'regulated5V2_copper_half', 'duty_replace_copper_half',
                              'regulated3V3_target101mA_copper_half', 'ideal_copper_floor']:
        continue
    assert f"{float(p['sensor_voltage_V']):.6f}V" in text, p['architecture']
checks['report_primary_values_match_computation'] = True
whitespace = []
for p in [REPORT] + list(E.rglob('*')):
    if not p.is_file():
        continue
    if p != REPORT and 'inputs' in p.relative_to(E).parts:
        continue
    if p.suffix not in ['.md', '.py', '.json', '.csv']:
        continue
    for n, line in enumerate(p.read_text().splitlines(), 1):
        if line.rstrip() != line:
            whitespace.append([str(p.relative_to(R)), n])
assert not whitespace, whitespace
checks['authored_whitespace_pass'] = True
now = datetime.datetime.now(datetime.timezone.utc)
deadline = datetime.datetime.fromisoformat(start['start']['deadline_utc'].replace('Z', '+00:00'))
assert now < deadline
save(E / 'verification.json', dict(status='PASS_REPRODUCTION_AND_PRESERVATION_ONLY',
                                  verified_utc=now.isoformat(), deadline_utc=deadline.isoformat(), checks=checks))
files = [REPORT] + sorted(p for p in E.rglob('*') if p.is_file() and p.name != 'manifest.json')
save(E / 'manifest.json', {str(p.relative_to(R)): digest(p) for p in files})
print(json.dumps(checks, indent=2))
