"""Conditional continuation after the retained normal-circuit capture.

Run once in the prepared /tmp/eda004f environment. Unexpected acceptance
results persist a terminal stop before any next generation.
"""
import json
from pathlib import Path
from capture import run, save, digest, utc

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / 'evidence'
BASE = Path('/tmp/eda004f')
PYTHON = str(BASE / 'venv/bin/python')
CLI = str(BASE / 'kicad/usr/bin/kicad-cli')
ENV = json.loads((EVIDENCE / 'kicad-env.json').read_text())
CONTRACT = json.loads((ROOT / 'contract.json').read_text())


def stop(reason):
    save(EVIDENCE / 'stop-decision.json', dict(recorded_utc=utc(), reason=reason, additional_experiments_forbidden=True))
    raise RuntimeError(reason)


def accept(case, result, erc_record):
    exp = CONTRACT['normal' if case == 'fresh' else case]
    violations = result['erc_violations']
    ok = erc_record['exit_code'] == exp.get('erc_exit', 0)
    if case in ('normal', 'fresh', 'value'):
        ok = ok and result['parity_pass'] and not violations
    else:
        ok = ok and result['parity_pass'] is False
        ok = ok and all(t in [v['type'] for v in violations] for t in exp['required_erc_types'])
        ok = ok and any(f['category'] == 'xml-net' and f['detail'] == exp['required_net_mismatch_endpoint'] for f in result['failures'])
        # Require the actual targeted pin(s), identified by KiCad item text.
        refpins = [exp['required_erc_endpoint']] if case == 'disconnect' else exp['required_erc_endpoints']
        targeted = [v for v in violations if v['type'] in exp['required_erc_types']]
        for endpoint in refpins:
            ref, pin = endpoint.split('.')
            ok = ok and any(f'Symbol {ref} ' in i['description'] and f'Pin {pin} ' in i['description'] for v in targeted for i in v['items'])
        # No unrelated semantic loss is tolerated in the negative copies.
        allowed = {'source-net', 'xml-net'} | ({'nc-marker'} if case == 'conflict' else set())
        ok = ok and all(f['category'] in allowed and f['detail'] == exp['required_net_mismatch_endpoint'] for f in result['failures'])
        ok = ok and all(v['severity'] == 'error' for v in violations)
    save(EVIDENCE / f'{case}-acceptance.json', dict(recorded_utc=utc(), all_conditions_pass=bool(ok), erc_exit_code=erc_record['exit_code'], result=result))
    if not ok:
        stop(f'{case}: fixed acceptance conditions not met')


def capture_case(case):
    dest = BASE / case
    dest.mkdir(exist_ok=False)
    assert not list(dest.iterdir())
    save(EVIDENCE / f'{case}-start.json', dict(recorded_utc=utc(), directory=str(dest), initially_empty=True, same_prepared_environment=True))
    run(case + '-generate', [PYTHON, '-B', str(ROOT / 'generate.py'), str(dest), '--case', 'normal' if case == 'fresh' else case], dest, artifacts=[('fixture.kicad_sch', dest / 'fixture.kicad_sch')])
    run(case + '-netlist', [CLI, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', str(dest / 'fixture.xml'), str(dest / 'fixture.kicad_sch')], dest, env=ENV, artifacts=[('fixture.xml', dest / 'fixture.xml')])
    name = case + '-erc'
    try:
        record = run(name, [CLI, 'sch', 'erc', '--format', 'json', '--severity-all', '--exit-code-violations', '-o', str(dest / 'erc.json'), str(dest / 'fixture.kicad_sch')], dest, env=ENV, artifacts=[('erc.json', dest / 'erc.json')])
    except RuntimeError:
        record = json.loads((EVIDENCE / 'processes' / name / 'record.json').read_text())
        if case not in ('disconnect', 'conflict') or record['exit_code'] != CONTRACT[case]['erc_exit']:
            stop(f'{case}: unexpected KiCad process failure')
    run(case + '-reconcile', [PYTHON, '-B', str(ROOT / 'reconcile.py'), str(dest), '--case', 'normal' if case == 'fresh' else case, '--output', str(dest / 'reconciliation.json')], dest, artifacts=[('reconciliation.json', dest / 'reconciliation.json')])
    result = json.loads((dest / 'reconciliation.json').read_text())
    accept(case, result, record)
    return result


if __name__ == '__main__':
    assert digest(ROOT / 'contract.json') == json.loads((EVIDENCE / 'contract-freeze.json').read_text())['contract_sha256']
    normal = json.loads((BASE / 'normal/reconciliation.json').read_text())
    accept('normal', normal, json.loads((EVIDENCE / 'processes/normal-erc-configured/record.json').read_text()))
    for case in ('disconnect', 'conflict'):
        capture_case(case)
        print(case + ': accepted detection')
    value = capture_case('value')
    wanted = json.loads(json.dumps(normal['normalized']))
    wanted['components']['R1']['value'] = '12k'
    if value['normalized'] != wanted:
        stop('value: changes beyond R1 value')
    save(EVIDENCE / 'value-diff.json', dict(only_semantic_change={'R1.value': ['10k', '12k']}, all_conditions_pass=True))
    fresh = capture_case('fresh')
    if fresh['normalized'] != normal['normalized']:
        stop('fresh: semantic difference')
    save(EVIDENCE / 'fresh-comparison.json', dict(recorded_utc=utc(), semantic_equal=True, normal_sha256=digest(BASE / 'normal/fixture.kicad_sch'), fresh_sha256=digest(BASE / 'fresh/fixture.kicad_sch'), same_environment=True, full_environment_rebuild=False))
    save(EVIDENCE / 'terminal-result.json', dict(recorded_utc=utc(), classification='SMALL_SCHEMATIC_CANDIDATE_PASS', initial_acceptance='FAIL: library configuration warnings', configured_normal='PASS', negative_detection='PASS', value_change='PASS', empty_directory_regeneration='PASS', main_pcb_routing_manufacturing_adoption='NOT ENTERED'))
