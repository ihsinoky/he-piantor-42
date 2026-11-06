"""Verify the Stage 1 evidence without modifying any input or existing board."""
from pathlib import Path
import datetime
import gzip
import hashlib
import json
import os
import re
import subprocess
import sys

E = Path(__file__).resolve().parent
ROOT = E.parents[3]
REPORT = ROOT / 'docs/issue-158-vera-wing-stage1.md'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    with gzip.open(E/'protected-start.json.gz','rt') as f:
        protected = json.load(f)
    changed = {p:'missing' if not (ROOT/p).is_file() else 'hash differs'
               for p,h in protected.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h}
    inputs = json.loads((E/'inputs.json').read_text())['files']
    input_changes = [p for p,r in inputs.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=r['sha256']]
    reproduced = subprocess.run([sys.executable,str(E/'analyze.py')],capture_output=True,check=True).stdout
    identical = reproduced == (E/'analysis.json').read_bytes()
    missing = []
    checked = 0
    # Input .txt snapshots preserve their source link spelling intentionally.
    for doc in [REPORT,E/'README.md']:
        for target in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
            if '://' in target or target.startswith('#'):
                continue
            checked += 1
            path = (doc.parent/target.split('#')[0]).resolve()
            if not path.exists():
                missing.append(str(path))
    base = json.loads((E/'start.json').read_text())['base']
    env = os.environ.copy()
    env.setdefault('GIT_DIR',str(ROOT/'.issue158-runtime/git'))
    env.setdefault('GIT_WORK_TREE',str(ROOT))
    delta = subprocess.check_output(['git','diff',base,'--name-status','--'],env=env,cwd=ROOT,text=True)
    staged_or_committed = [line.split('\t',1) for line in delta.splitlines()]
    allowed_prefix = str(E.relative_to(ROOT))+'/'
    invalid = [r for r in staged_or_committed if r[0]!='A' or
               not (r[1]=='docs/issue-158-vera-wing-stage1.md' or r[1].startswith(allowed_prefix))]
    forbidden = [str(p.relative_to(E)) for p in E.rglob('*') if p.is_file() and
                 p.suffix in {'.kicad_pcb','.kicad_mod','.kicad_sch','.gbr','.drl','.step'}]
    trailing = []
    for p in [REPORT,*[p for p in E.rglob('*') if p.is_file() and p.suffix in {'.py','.md','.json','.txt'}]]:
        if p.suffix=='.txt':  # exact original snapshots are not rewritten
            continue
        for i,line in enumerate(p.read_text().splitlines(),1):
            if line.rstrip()!=line:
                trailing.append(f'{p.relative_to(ROOT)}:{i}')
    result={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'protected_count':len(protected),'protected_changes':changed,'input_changes':input_changes,
            'analysis_byte_identical':identical,'local_links_checked':checked,'missing_links':missing,
            'base':base,'diff_entries':staged_or_committed,'invalid_changes':invalid,
            'new_board_or_manufacturing_files':forbidden,'trailing_whitespace':trailing,
            'not_run':['routing','DRC','CAD generation','physical tests','orders','payments','merge']}
    result['passed']=not any([changed,input_changes,not identical,missing,invalid,forbidden,trailing])
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['passed'] else 1


if __name__=='__main__':
    raise SystemExit(main())
