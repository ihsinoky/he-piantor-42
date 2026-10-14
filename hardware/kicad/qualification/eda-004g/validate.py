"""Verify saved evidence/scope after STOP. No EDA generation or routing."""
import base64
import gzip
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
EV = ROOT / 'evidence'
BASELINE = '4a96d6ff6ddca3fd19330e392ae8cf91c39f6b6c'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(directory,name):
    p = directory/name
    return p.read_bytes() if p.exists() else gzip.decompress(p.with_name(name+'.gz').read_bytes())


def validate():
    records = []
    for directory in sorted((EV/'processes').iterdir()):
        record = json.loads((directory/'record.json').read_text())
        assert record['end_utc'] and record['exit_code'] is not None and not record['timed_out']
        assert record['display_unset']
        assert record['stdout_sha256'] == sha(read(directory,'stdout')), directory
        assert record['stderr_sha256'] == sha(read(directory,'stderr')), directory
        for item in record['artifacts']:
            if item['present']:
                assert sha((EV/item['saved_path']).read_bytes()) == item['sha256']
        records.append(record)
    idx = json.loads((EV/'package-extractions-index.json').read_text())
    assert sha((EV/idx['path']).read_bytes()) == idx['sha256']
    extractions = json.loads(gzip.decompress((EV/idx['path']).read_bytes()))
    assert len(extractions) == idx['count']
    for item in extractions:
        r = item['record']
        assert r['exit_code'] == 0 and r['end_utc'] and not r['timed_out']
        assert r['stdout_sha256'] == sha(base64.b64decode(item['stdout_base64']))
        assert r['stderr_sha256'] == sha(base64.b64decode(item['stderr_base64']))
        records.append(r)
    freeze = json.loads((EV/'input-freeze.json').read_text())
    assert freeze['all_inputs_match'] and freeze['main_commit'] == BASELINE
    for x in freeze['inputs']:
        assert sha((REPO/x['path']).read_bytes()) == x['expected_sha256']
        assert sha(subprocess.check_output(['git','show',f"{BASELINE}:{x['path']}"],cwd=REPO)) == x['expected_sha256']
    partial = json.loads((EV/'partial-expectation-freeze.json').read_text())
    assert partial['sha256'] == sha((ROOT/'source-intent.partial.json').read_bytes())
    corrected = json.loads((EV/'model-probe-correction-freeze.json').read_text())
    assert corrected['probe_sha256'] == sha((ROOT/'assess-public-models.py').read_bytes())
    assert corrected['source_inventory_sha256'] == partial['sha256']
    record = json.loads((EV/'processes/public-model-assessment-corrected/record.json').read_text())
    assert partial['recorded_utc'] < corrected['recorded_utc'] < record['start_utc']
    first = json.loads((EV/'processes/public-model-assessment/public-model-assessment.json').read_text())
    final = json.loads((EV/'public-model-assessment.json').read_text())
    assert first['missing_model_public_add_probe']['exception_type'] == 'ValidationError'
    assert final['missing_model_public_add_probe']['exception_type'] == 'LibraryError'
    assert final == json.loads((EV/'processes/public-model-assessment-corrected/public-model-assessment.json').read_text())
    assert not final['exact_lookup']['U_LOAD']['available']
    for name,digest in final['symbol_file_sha256'].items():
        assert sha(gzip.decompress((ROOT/'library'/f'{name}.gz').read_bytes())) == digest
    stop = json.loads((EV/'stop-decision.json').read_text())
    assert stop['classification'] == 'CONVERSION_BLOCKED'
    assert all(v is None for v in stop['main_metrics'].values())
    assert stop['main_initial_attempts'] == stop['main_confirmation_attempts'] == stop['small_transport_attempts'] == 0
    assert not json.loads((EV/'attempt-ledger.json').read_text())['attempts']
    assert not json.loads((EV/'checker-coverage.json').read_text())['main_checker_qualified']
    assert all(t['result'] == 'NOT ENTERED' and not t['qualified'] for t in json.loads((EV/'checker-coverage.json').read_text())['required_main_fault_tests'])
    assert all(r['end_utc'] < stop['recorded_utc'] for r in records), 'EDA process launched after STOP'
    # Corroborate individual source intent from historical evidence again, read-only.
    spec = importlib.util.spec_from_file_location('retained',ROOT/'compare-retained-intent.py')
    module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    assert module.compare() == json.loads((EV/'retained-intent-comparison.json').read_text())
    assert not list(ROOT.rglob('*.kicad_pcb')) and not list(ROOT.rglob('*.kicad_sch'))
    assert not list(ROOT.rglob('*.dsn')) and not list(ROOT.rglob('*.ses'))
    changed = subprocess.check_output(['git','diff','--name-only',BASELINE],cwd=REPO,text=True).splitlines()
    untracked = subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=REPO,text=True).splitlines()
    allowed = ['hardware/kicad/qualification/eda-004g/', 'docs/native-main-routing-qualification.md',
               'docs/project-status.md','docs/eda-path-history.md','task/data/project-status.js']
    assert all(any(p == a or p.startswith(a) for a in allowed) for p in changed+untracked), changed+untracked
    immutable = json.loads((EV/'immutable-sha256.json').read_text())
    for name,digest in immutable.items():
        assert sha((ROOT/name).read_bytes()) == digest, name
    return dict(saved_process_records=len(records), compressed_extraction_records=len(extractions),
        raw_hashes_pass=True, frozen_inputs_and_partial_expectation_pass=True,
        original_and_corrected_probe_results_distinguished=True,
        individual_retained_intent_corroboration='PASS_WITH_LIMITS',
        main_fault_detection='NOT ENTERED / UNQUALIFIED', main_metrics_all_null=True,
        no_routes_or_post_stop_eda_processes=True, prior_evidence_decisions_product_ci_unchanged=True,
        changed_scope_only=True)


if __name__ == '__main__':
    result=validate()
    (EV/'submission-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
