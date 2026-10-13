"""Replay immutable saved evidence; launch no KiCad/generator experiments."""
import gzip
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from reconcile import reconcile

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
EVIDENCE = ROOT / 'evidence'
BASELINE = '3ed5558855c7d95951ea4a728f755707061279b4'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def raw(directory, name):
    path = directory / name
    return path.read_bytes() if path.exists() else gzip.decompress(path.with_name(name + '.gz').read_bytes())


def validate():
    records = []
    for directory in sorted((EVIDENCE / 'processes').iterdir()):
        record = json.loads((directory / 'record.json').read_text())
        assert record['end_utc'] and record['exit_code'] is not None
        assert record['display_unset'] and not record['timed_out']
        assert record['stdout_sha256'] == sha(raw(directory, 'stdout')), directory
        assert record['stderr_sha256'] == sha(raw(directory, 'stderr')), directory
        for artifact in record['artifacts']:
            if artifact['present']:
                assert sha((EVIDENCE / artifact['saved_path']).read_bytes()) == artifact['sha256']
        records.append(record)
    frozen = json.loads((EVIDENCE / 'contract-freeze.json').read_text())
    assert sha((ROOT / 'contract.json').read_bytes()) == frozen['contract_sha256']
    assert sha((ROOT / 'generate.py').read_bytes()) == frozen['generator_sha256']
    assert frozen['frozen_utc'] < json.loads((EVIDENCE / 'processes/normal-generate/record.json').read_text())['start_utc']
    manifest = json.loads((EVIDENCE / 'immutable-sha256.json').read_text())
    for name, digest in manifest.items():
        assert sha((ROOT / name).read_bytes()) == digest, name
    for name, digest in frozen['preparation']['symbol_hashes'].items():
        assert sha(raw(ROOT / 'library', name)) == digest, name
    initial = json.loads((EVIDENCE / 'processes/normal-erc/erc.json').read_text())
    violations = [v for s in initial['sheets'] for v in s['violations']]
    assert len(violations) == 6
    assert all(v['type'] == 'lib_symbol_issues' and v['severity'] == 'warning' for v in violations)
    correction = json.loads((EVIDENCE / 'configuration-correction.json').read_text())
    schematic = EVIDENCE / 'processes/normal-generate/fixture.kicad_sch'
    assert correction['before_schematic_sha256'] == sha(schematic.read_bytes())
    assert (EVIDENCE / 'processes/normal-generate/sym-lib-table').read_bytes() == (EVIDENCE / 'processes/normal-erc-configured/sym-lib-table').read_bytes()
    results = {}
    for case in ['normal', 'disconnect', 'conflict', 'value', 'fresh']:
        with tempfile.TemporaryDirectory(prefix='eda004f-evidence-replay-') as directory:
            d = Path(directory)
            for filename, process in [('fixture.kicad_sch', case + '-generate'), ('fixture.xml', case + '-netlist'), ('erc.json', 'normal-erc-configured' if case == 'normal' else case + '-erc')]:
                (d / filename).write_bytes((EVIDENCE / 'processes' / process / filename).read_bytes())
            result = reconcile(d, 'normal' if case == 'fresh' else case)
        stored = json.loads((EVIDENCE / 'processes' / (case + '-reconcile') / 'reconciliation.json').read_text())
        assert result == stored, case
        acceptance = json.loads((EVIDENCE / (case + '-acceptance.json')).read_text())
        assert acceptance['all_conditions_pass'] and acceptance['result'] == result
        expected_exit = 5 if case in ('disconnect', 'conflict') else 0
        assert acceptance['erc_exit_code'] == expected_exit
        if case in ('normal', 'value', 'fresh'):
            assert result['parity_pass'] and not result['erc_violations']
        else:
            endpoint = 'U2.2' if case == 'disconnect' else 'U2.4'
            assert not result['parity_pass']
            assert any(f == dict(category='xml-net', detail=endpoint) for f in result['failures'])
            required = 'pin_not_connected' if case == 'disconnect' else 'pin_to_pin'
            assert any(v['type'] == required for v in result['erc_violations'])
        results[case] = result
    assert results['normal']['normalized'] == results['fresh']['normalized']
    expected = json.loads(json.dumps(results['normal']['normalized']))
    expected['components']['R1']['value'] = '12k'
    assert expected == results['value']['normalized']
    assert results['normal']['source_pin_count'] == 16 and results['normal']['xml_pin_count'] == 14
    assert json.loads((EVIDENCE / 'file-comparison.json').read_text())['fresh']['uuid_normalized_bytes_equal']
    allowed = ['hardware/kicad/qualification/eda-004f/', 'docs/headless-schematic-qualification.md', 'docs/project-status.md', 'docs/eda-path-history.md', 'task/data/project-status.js']
    changed = subprocess.check_output(['git', 'diff', '--name-only', BASELINE], cwd=REPO, text=True).splitlines()
    untracked = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=REPO, text=True).splitlines()
    assert all(any(p == a or p.startswith(a) for a in allowed) for p in changed + untracked), changed + untracked
    print(json.dumps(dict(saved_process_records=len(records), replayed_cases=list(results), frozen_contract=True, raw_hashes=True, prior_evidence_and_decisions_unchanged=True, changed_scope_only=True), indent=2))


if __name__ == '__main__':
    validate()
