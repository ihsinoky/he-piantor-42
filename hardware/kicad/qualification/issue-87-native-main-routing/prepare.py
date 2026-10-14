"""Issue 87: reuse the pinned installer; never execute historical epoch drivers."""
import os, sys, runpy, json, hashlib, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[3]
BASE=Path('/tmp/issue87')
OLD=ROOT.parent/'eda-004g/resume-02'
os.environ['EDA004D_EVIDENCE_DIR']=str(ROOT/'evidence')
os.environ['EDA004D_WORK_DIR']=str(BASE)
sys.path.insert(0,str(REPO/'hardware/tscircuit/qualification/eda-004d'))
from process import run,save,digest,utc
if __name__=='__main__':
    BASE.mkdir(exist_ok=False)
    save(ROOT/'evidence/start.json',dict(start_utc='2026-10-14T20:46:26Z',cwd=str(REPO),branch_at_start='main',head_at_start='49ebe146a586bf820a747b93951a29fe94f08623',worktree_at_start='clean',branch='issue-87-native-main-routing',fetched_main='49ebe146a586bf820a747b93951a29fe94f08623',six_hour_deadline='2026-10-15T02:46:26Z',experiment_cutoff='2026-10-15T02:16:26Z',authority='Issue #87 and current PO instruction only; no inherited resume authority'))
    files=[p for p in OLD.rglob('*') if p.is_file()]
    freeze={str(p.relative_to(REPO)):digest(p) for p in files}
    for name in ['initial-author-pcb-explicit-public-library-io','initial-author-schematic','initial-netlist','initial-read-pcb']:
        record=json.loads((OLD/'evidence/processes'/name/'record.json').read_text())
        for item in record['artifacts']:
            if item['present']:assert digest(OLD/'evidence'/item['saved_path'])==item['sha256']
    assert digest(OLD/'main-contract-v2.json')==json.loads((OLD/'evidence/contracts-freeze.json').read_text())['main']
    save(ROOT/'evidence/reuse-hashes.json',dict(commit='49ebe146a586bf820a747b93951a29fe94f08623',files=freeze))
    runpy.run_path(str(REPO/'hardware/tscircuit/qualification/eda-004d/install-kicad.py'),run_name='__main__')
    run('venv',['/usr/bin/python3','-m','venv','--system-site-packages',str(BASE/'venv')],BASE)
    run('geometry-install',[str(BASE/'venv/bin/pip'),'install','--require-hashes','-r',str(OLD/'geometry-requirements.txt')],BASE,180)
    print('environment ready')
