"""Read-only immutable/current-main input comparison, before Main authoring."""
import platform
import subprocess
from pathlib import Path
from capture import ROOT, run, save, digest, utc

REPO = ROOT.parents[3]
EV = ROOT / 'evidence'
BASELINE = 'b84585ecc2cf32000285bbf389d9fea255436980'
START = '4a96d6ff6ddca3fd19330e392ae8cf91c39f6b6c'
FILES = {
    'src/qualification/revm1-routing-proof.tsx': '0caa8e53eed298c3cf65715a15a1d671d91de715d4eb8f790eeb13e17a777008',
    'src/qualification/JstGh14.tsx': 'ad23f75d53a917f8f43485b7fe887ff096ab0bdda244e3dc6e44fd73d93c787c',
    'src/qualification/native-support-footprints.tsx': '7b0efff9f5178b589c2ef7085625549bc4701ee24d2841ee24d2841ee7b46785921db55fe',
    'src/components/HallKey.tsx': '0241daa3e2640bc870537ba3fa6571868858345f361456d80f73849dad32495c',
    'qualification/eda-003c/latest-stock/package-lock.json': 'dec21cc020344ce8c8a769bd3ec92d99186546034974bcb702fc68f9dd7a455f',
}
# Literal plan transcription; corrected here before the first freeze execution.
FILES['src/qualification/native-support-footprints.tsx'] = '7b0efff9f5178b589c2ef7085625549bc4701ee24d2841ee7b46785921db55fe'

if __name__ == '__main__':
    import hashlib
    records = []
    for path, expected in FILES.items():
        relative = 'hardware/tscircuit/' + path
        data = subprocess.check_output(['git', 'show', f'{BASELINE}:{relative}'], cwd=REPO)
        main = subprocess.check_output(['git', 'show', f'{START}:{relative}'], cwd=REPO)
        record = dict(path=relative, expected_sha256=expected,
                      immutable_sha256=hashlib.sha256(data).hexdigest(),
                      main_sha256=hashlib.sha256(main).hexdigest(),
                      worktree_sha256=digest(REPO / relative))
        assert all(record[k] == expected for k in ('immutable_sha256', 'main_sha256', 'worktree_sha256')), record
        records.append(record)
    save(EV / 'input-freeze.json', dict(recorded_utc=utc(), immutable_commit=BASELINE, main_commit=START, all_inputs_match=True, inputs=records))
    save(EV / 'session-start.json', dict(start_utc='2026-10-14T01:17:56+00:00', experiment_cutoff_utc='2026-10-14T06:47:56+00:00', absolute_deadline_utc='2026-10-14T07:17:56+00:00', cwd=str(REPO), branch='eda-004g-native-main-routing-qualification', head=START, initial_worktree_clean=True, prior_cumulative_ai_estimate_h=3.286, human_review_effort_h=None, previous_permissions_inherited=False, issue_updated_at='2026-10-14T01:13:12Z'))
    run('record-host', ['python3', '-c', 'import platform,sys; print(platform.platform()); print(sys.version)'], REPO)
    run('record-java', ['java', '-version'], REPO)
    run('record-node', ['node', '--version'], REPO)
    run('record-npm', ['npm', '--version'], REPO)
    print('immutable/current-main/worktree hashes PASS')
