"""PO-authorized Issue87 resume; historical STOP evidence stays immutable."""
import os,sys,json,hashlib,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PREV=ROOT.parent
REPO=ROOT.parents[4]
OLD=PREV.parent/'eda-004g/resume-02'
BASE=Path('/tmp/issue87-resume01')
ENV=json.loads((PREV/'evidence/kicad-env.json').read_text())
JAVA=Path('/home/codespace/java/21.0.12+1-ms/bin/java')
JAR=Path('/tmp/issue87/freerouting.jar')
GEOM=Path('/tmp/issue87/geometry/bin/python')
CLI=Path('/tmp/issue87/kicad/usr/bin/kicad-cli')
os.environ['EDA004D_EVIDENCE_DIR']=str(ROOT/'evidence')
sys.path.insert(0,str(REPO/'hardware/tscircuit/qualification/eda-004d'))
from process import run,save,digest,utc
if __name__=='__main__':
    BASE.mkdir(exist_ok=False)
    files=subprocess.check_output(['git','ls-files','-z',str(PREV.relative_to(REPO))],cwd=REPO).decode().split('\0')
    frozen={f:digest(REPO/f) for f in files if f}
    assert digest(JAR)=='2c07d58f75dac03782664081e7a58b41c25400d871a9fcf166a2ea6fe60d5def'
    for name in ['smoke','main']:
        old=json.loads((PREV/'evidence/processes'/('smoke-dsn' if name=='smoke' else 'main-dsn')/'record.json').read_text())
        a=next(a for a in old['artifacts'] if a['label']=='input.dsn');assert digest(Path('/tmp/issue87')/name/'input.dsn')==a['sha256']
    save(ROOT/'evidence/start.json',dict(start_utc='2026-10-14T21:13:54Z',cwd=str(REPO),branch='issue-87-native-main-routing',head='47bb0e62f4e60b469139bd4584383e67f5de8eaf',remote_head_identical=True,worktree='clean',prior_charge_seconds=780,budget_total_seconds=21600,one_hour_checkpoint_utc='2026-10-14T22:00:54Z',experiment_cutoff_utc='2026-10-15T02:30:54Z',session_deadline_utc='2026-10-15T03:00:54Z',session_gap='Prior closing tool observation20:59:18Z to21:13:54Z=14m36s; approximate PO/session wait, not charged; prior conservative13m remains charged. Prior final-response boundary not independently measured.'))
    save(ROOT/'evidence/preserved-files.json',frozen)
    print('reuse hashes and session recorded',len(frozen))
