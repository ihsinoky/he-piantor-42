"""Recorded pre-route replay procedure; never run as part of post-STOP validation.

Requires separate authorization to execute. Defaults to describing the procedure.
Uses new caller-specified work/evidence directories, retained source and exact locks.
No router, Main, generated-KiCad repair or experimental retry is implemented.
"""
import argparse, os, shutil, sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--execute', action='store_true')
parser.add_argument('--work-dir', type=Path)
parser.add_argument('--evidence-dir', type=Path)
args = parser.parse_args()
if not args.execute:
    print('Plan: verify references; extract retained upstream; apply bounded patch; '
          'install exact locked runtime/build dependencies; build kicadts/converter; '
          'extract KiCad 9.0.9; unit tests; unchanged raw conversion; read-only '
          'inventory/DRC/ERC; reconciliation; terminal STOP. No routing.')
    sys.exit(0)
if not args.work_dir or not args.evidence_dir:
    parser.error('--execute requires fresh --work-dir and --evidence-dir')
base = args.work_dir.resolve()
evidence = args.evidence_dir.resolve()
if base.exists() or evidence.exists():
    parser.error('work and evidence directories must not exist')
os.environ['EDA004D_WORK_DIR'] = str(base)
os.environ['EDA004D_EVIDENCE_DIR'] = str(evidence)
from process import ROOT, run, save, digest, utc
import json

references = json.loads((ROOT / 'evidence/references.json').read_text())
repo = ROOT.parents[3]
for name, sha in references['files'].items():
    assert digest(repo / name) == sha, name
base.mkdir(parents=True)
evidence.mkdir(parents=True)
save(evidence / 'attempt-ledger.json', {'attempts': [],
    'initial_all_conditions_pass': False, 'main_attempts': 0})
archive = ROOT / 'evidence/processes/converter-source-download/converter-source.tar.gz'
expected = json.loads((ROOT / 'evidence/upstream-source-manifest.json').read_text())
assert digest(archive) == expected['archive_sha256']
run('converter-source-extract', ['tar', '-xzf', str(archive), '-C', str(base)], base)
source = base / 'circuit-json-to-kicad-8dee5b926f5db28800292b46b66a712c71aba055'
for name, sha in expected['files'].items():
    assert digest(source / name) == sha, name
shutil.copytree(source, base / 'patched-converter')
run('bounded-patch-apply', ['patch', '-p1', '--input', str(ROOT / 'converter.patch')],
    base / 'patched-converter')
patch = json.loads((ROOT / 'evidence/patch-provenance.json').read_text())
assert digest(ROOT / 'converter.patch') == patch['patch_sha256']
for name, hashes in patch['files'].items():
    assert digest(base / 'patched-converter' / name) == hashes['patched_sha256']
prior = ROOT.parent / 'eda-004c'
(base / 'kicadts').mkdir()
(base / 'runtime').mkdir()
shutil.copyfile(prior / 'kicadts-build-package-lock.json', base / 'kicadts/package-lock.json')
for name in ['package.json', 'package-lock.json']:
    shutil.copyfile(prior / ('converter-' + name), base / 'runtime' / name)
for script, timeout in [('setup-js.py', 900), ('build-converter.py', 240),
                        ('install-kicad.py', 1200), ('evaluate.py', 480),
                        ('reconcile.py', 120)]:
    run('replay-' + script.removesuffix('.py'), [sys.executable, '-B', str(ROOT / script)],
        ROOT, timeout)
save(evidence / 'stop-decision.json', {'recorded_utc': utc(),
    'classification': 'CONVERSION_BLOCKED',
    'first_failure_gate': 'D1_FOOTPRINT_LIBRARY_ID_COLLISION',
    'reason': 'Recorded pre-route failure reproduced; no router or retry.'})
