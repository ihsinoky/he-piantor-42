"""Read-only deliverable integrity checks; never install/build/convert/route."""
from process import *
import ast, gzip, subprocess

BASELINE = '6684821a00bc2ebe368dcc78495d013eb5dd47d9'
REPO = ROOT.parents[3]


def decoded(path):
    if path.is_file():
        return path.read_bytes()
    return gzip.decompress(Path(str(path) + '.gz').read_bytes())


def check_outcome(outcome, pre, ledger):
    assert outcome['classification'] == 'CONVERSION_BLOCKED'
    assert outcome['first_failure_gate'] == 'D1_FOOTPRINT_LIBRARY_ID_COLLISION'
    assert outcome['pre_route_status'] == 'FAIL'
    assert outcome['initial_status'] == outcome['fresh_status'] == 'NOT ENTERED'
    assert outcome['route_attempts'] == {'initial': 0, 'fresh': 0, 'main': 0}
    assert all(value is None for key in ('initial', 'fresh') for value in outcome[key].values())
    for key in ('real_output_output_erc_detection', 'independent_full_physical_checker', 'reproducibility'):
        assert outcome[key] is None
    assert pre['all_conditions_pass'] is False
    assert pre['status'] == 'FAIL' and pre['limited_object_parity'] == 'PASS'
    assert pre['erc_errors'] == 3 and pre['erc_warnings'] == 16
    assert pre['drc_errors'] == 0 and pre['drc_warnings'] == 2
    assert pre['pre_route_intentional_unconnected'] == 2
    assert pre['real_output_output_fault_erc'] is None
    assert ledger['attempts'] == [] and ledger['initial_all_conditions_pass'] is False


def validate():
    protected = json.loads((EVIDENCE / 'protected-start.json').read_text())
    for name, sha in protected.items():
        assert digest(REPO / name) == sha, name
        blob = subprocess.check_output(['git', 'show', BASELINE + ':' + name], cwd=REPO)
        assert hashlib.sha256(blob).hexdigest() == sha, name
    references = json.loads((EVIDENCE / 'references.json').read_text())
    assert references['commit'] == BASELINE
    for name, sha in references['files'].items():
        assert digest(REPO / name) == sha, name
    patch = json.loads((EVIDENCE / 'patch-provenance.json').read_text())
    assert patch['upstream_git'] == '8dee5b926f5db28800292b46b66a712c71aba055'
    assert digest(ROOT / 'converter.patch') == patch['patch_sha256']
    assert set(patch['files']) == {'lib/pcb/stages/AddFootprintsStage.ts',
        'lib/schematic/getLibraryId.ts', 'lib/schematic/stages/utils/createPinSubsymbol.ts'}
    import tarfile
    source = json.loads((EVIDENCE / 'upstream-source-manifest.json').read_text())
    archive = EVIDENCE / 'processes/converter-source-download/converter-source.tar.gz'
    assert digest(archive) == source['archive_sha256']
    with tarfile.open(archive) as tar:
        prefix = 'circuit-json-to-kicad-' + patch['upstream_git'] + '/'
        for name, hashes in patch['files'].items():
            assert hashlib.sha256(tar.extractfile(prefix + name).read()).hexdigest() == hashes['original_sha256']
    assert set(source['changed_source_files']) == set(patch['files'])
    runtime = json.loads((EVIDENCE / 'runtime-provenance.json').read_text())
    prior = ROOT.parent / 'eda-004c'
    assert runtime['converter_lock'] == digest(prior / 'converter-package-lock.json')
    assert runtime['kicadts_build_lock'] == digest(prior / 'kicadts-build-package-lock.json')
    assert runtime['kicadts_dist'] == '4dbc65bfc8f29de901eba9252d9cbd02e9ae9e1b08f16142158cd252fb6fa783'
    stop = json.loads((EVIDENCE / 'stop-decision.json').read_text())
    records = list((EVIDENCE / 'processes').glob('*/record.json'))
    for file in records:
        rec = json.loads(file.read_text())
        assert rec['exit_code'] == 0 and not rec['timed_out'], file
        assert rec['start_utc'] <= rec['end_utc']
        for stream in ('stdout', 'stderr'):
            assert hashlib.sha256(decoded(file.parent / stream)).hexdigest() == rec[stream + '_sha256']
        for artifact in rec['artifacts']:
            assert artifact['present'] is True
            assert hashlib.sha256(decoded(EVIDENCE / artifact['saved_path'])).hexdigest() == artifact['sha256']
        if not file.parent.name.startswith(('verify-', 'record-', 'git-', 'ci-')):
            assert rec['end_utc'] < stop['recorded_utc'], file
        assert '-de' not in rec['command'] and '-do' not in rec['command']
        assert not any('freerouting' in word.lower() for word in rec['command'])
    for item in json.loads((EVIDENCE / 'raw-preservation.json').read_text()).values():
        compressed = EVIDENCE / item['compressed_path']
        assert digest(compressed) == item['compressed_sha256']
        assert hashlib.sha256(gzip.decompress(compressed.read_bytes())).hexdigest() == item['uncompressed_sha256']
    outcome = json.loads((EVIDENCE / 'final-classification.json').read_text())
    pre = json.loads((EVIDENCE / 'pre-route-acceptance.json').read_text())
    ledger = json.loads((EVIDENCE / 'attempt-ledger.json').read_text())
    check_outcome(outcome, pre, ledger)
    assert json.loads((EVIDENCE / 'run-contract.json').read_text())['frozen'] is False
    assert json.loads((EVIDENCE / 'library-assessment.json').read_text())['status'] == 'FAIL'
    assert json.loads((EVIDENCE / 'boundary-reconciliation.json').read_text())['qualification_pass'] is False
    for name in ('test-patch.mjs', 'convert.mjs'):
        subprocess.run(['node', '--check', str(ROOT / name)], check=True)
    for file in ROOT.glob('*.py'):
        ast.parse(file.read_text(), filename=str(file))
    paths = subprocess.check_output(['git', 'diff', '--name-only', BASELINE], cwd=REPO).decode().splitlines()
    assert all(name.startswith('hardware/tscircuit/qualification/eda-004d/') or
               name == 'docs/alternate-physical-backend-converter-repair.md' for name in paths)
    subprocess.run(['git', 'diff', '--check', BASELINE], cwd=REPO, check=True)
    print(f'Deliverable validation PASS: {len(protected)} protected files; {len(records)} process records. Qualification remains CONVERSION_BLOCKED.')


if __name__ == '__main__':
    validate()
