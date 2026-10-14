"""STOP-safe, read-only evidence organization. Runs no experiment."""
import gzip
import json
import shutil
from pathlib import Path
from capture import ROOT, save, digest, utc

EV = ROOT / 'evidence'
BASE = Path('/tmp/eda004g')

if __name__ == '__main__':
    assert (EV / 'stop-decision.json').exists()
    observation = json.loads((EV / 'public-model-assessment.json').read_text())
    lib = ROOT / 'library'
    lib.mkdir(exist_ok=False)
    for name, expected in observation['symbol_file_sha256'].items():
        source = BASE / 'symbols/usr/share/kicad/symbols' / name
        assert digest(source) == expected
        (lib / (name + '.gz')).write_bytes(gzip.compress(source.read_bytes(), mtime=0))
    license_path = BASE / 'symbols/usr/share/doc/kicad-symbols/LICENSE.md'
    shutil.copyfile(license_path, lib / 'LICENSE.md')
    # Public-library source/installed-code parity; no imports/experiments.
    installed = next((BASE / 'venv/lib').glob('python*/site-packages/kicad_sch_api'))
    source = BASE / 'library-source/kicad_sch_api'
    comparisons = {str(p.relative_to(source)): digest(p) == digest(installed / p.relative_to(source))
                   for p in source.rglob('*.py')}
    assert all(comparisons.values())
    save(EV / 'installed-source-parity.json', dict(recorded_utc=utc(), all_python_source_files_equal=True, files=comparisons,
        source_archive='../../eda-004f/evidence/library-source.tar.gz',
        archive_sha256=digest(ROOT.parent / 'eda-004f/evidence/library-source.tar.gz')))
    save(EV / 'checker-coverage.json', dict(recorded_utc=utc(), main_checker_qualified=False,
        predecessors=[
            dict(path='hardware/kicad/qualification/eda-004f/reconcile.py', sha256=digest(ROOT.parent / 'eda-004f/reconcile.py'),
                 supported='Frozen six-symbol/16-pin, unrotated wire-stub/local-label schematic + four-component/14-pin XML. No PCB copper reader.'),
            dict(path='hardware/kicad/qualification/eda-004e/inspect.py', sha256=digest(ROOT.parent / 'eda-004e/inspect.py'),
                 supported='Frozen R1/U1, seven pads, two local tracks, four outline edges, object fields and configured rule values. No general copper-island/rule-enforcement verifier.'),
            dict(path='hardware/tscircuit/scripts/revm1-physical-connectivity.ts', sha256=digest(ROOT.parents[2] / 'tscircuit/scripts/revm1-physical-connectivity.ts'),
                 supported='Circuit JSON actual copper geometry; not a KiCad reader. Separate reviewed adaptation and negative tests required.')],
        required_main_fault_tests=[dict(fault=f, result='NOT ENTERED', qualified=False) for f in (
            'wrong-net actual copper short', 'missing required physical pad',
            'duplicate-number land loses physical connection', 'effective 0.20 mm rule missing')],
        gaps=['Complete independent source pad/drill/shape/layer/rotation/outline map',
              'KiCad actual-copper shape extraction, islands and layer transitions',
              'NC obstacles and hole/boundary spacing', 'positive Main baseline and specific negative detections'],
        inference='These are implementation/coverage gaps, not observed Main routing violations. No predecessor is promoted to a Main verifier.'))
    save(EV / 'version-boundary.json', dict(recorded_utc=utc(),
        kicad_binary='9.0.9', kicad_binding='9.0.9-9.0.9~ubuntu24.04.1',
        kicad_package_sha256=digest(BASE / 'kicad.deb'),
        kicad_symbols_package_sha256=digest(BASE / 'kicad-symbols.deb'),
        schematic_library_commit='505bca23e91cf3fa6e3b66976e529e775eada3ba',
        schematic_library_dependency_lock='../../eda-004f/requirements-lock.txt',
        schematic_library_dependency_lock_sha256=digest(ROOT.parent / 'eda-004f/requirements-lock.txt'),
        frontend='Not installed or executed; source/isolated EDA-003C lock read-only',
        production_tscircuit='0.0.2646 UNCHANGED',
        host_java='Microsoft OpenJDK 25.0.4.1+1-LTS (record-java); not selected as a qualified router runtime',
        router_discovery=dict(candidate='Freerouting v2.1.0',
            source='https://raw.githubusercontent.com/freerouting/freerouting/v2.1.0/build.gradle',
            published_java_target='21',
            status='DISCOVERY ONLY: router artifact and compatible Java 21 distribution/build/hash NOT FROZEN or installed before STOP'),
        router_run_contract='NOT FROZEN; no timeout/passes/threads/seed selected, no route authorized by prerequisites',
        full_environment_confirmation='UNQUALIFIED; initial tool re-preparation is not confirmation of complete environment'))
    records = [json.loads(p.read_text()) for p in (EV / 'processes').glob('*/record.json')]
    prep = [r for r in records if r['command'][0] not in ('node','npm','java') and 'public-model-assessment' not in ' '.join(r['command']) and not (len(r['command']) > 1 and r['command'][1] == '-c')]
    save(EV / 'effort-ledger.json', dict(recorded_utc=utc(),
        session_start_utc='2026-10-14T01:17:56+00:00',
        experiment_end_utc=json.loads((EV / 'stop-decision.json').read_text())['recorded_utc'],
        issue_limit_h=6, report_reserve_h=.5, prior_known_cumulative_ai_estimate_h=3.286,
        current_ai_effort_allowance_h=.750, current_estimate_includes_report_submission_ci_reserve=True,
        known_cumulative_ai_estimate_h=4.036, nominal_16h_arithmetic_remainder_h=11.964,
        measured_active_engineer_h=None, historical_human_review_report_h=None, unattended_wall_clock_h=None,
        saved_process_elapsed_seconds=sum(r['elapsed_seconds'] for r in records),
        preparation_process_elapsed_seconds=sum(r['elapsed_seconds'] for r in prep),
        accounting='Clock observations/process elapsed/AI allowance are different measures. Process times overlap session work and are not added twice. Nominal remainder is not a certified remaining engineer-hour budget. No reset.'))
    print('STOP-safe evidence organization complete')
