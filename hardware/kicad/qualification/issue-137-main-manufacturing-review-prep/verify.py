"""Validate review artifacts and addition-only scope, from the repo root.

Writes verification.json and manifest.json only within this new evidence dir.
Full HTTP bodies are optional runtime inputs; source records remain portable.
"""
import collections
import csv
import datetime
from decimal import Decimal as D
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

BASE=Path('hardware/kicad/qualification/issue-137-main-manufacturing-review-prep')
REPORT=Path('docs/issue-137-main-manufacturing-review-prep.md')
COMMIT='8a4c3d321fca4880e62289c10d81af845f162bc5'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def git(*args): return subprocess.check_output(['git',*args],text=True).strip()
j=json.loads((BASE/'board-analysis.json').read_text())
assert j['board_vias']==66 and j['logged_count']==25 and j['front_paste_graphics']==197
for path,digest in j['inputs'].items(): assert sha(Path(path))==digest
rows=list(csv.DictReader((BASE/'via-observations.csv').open()))
assert len(rows)==25 and len({r['via_uuid'] for r in rows})==25
categories=dict(collections.Counter(r['category'] for r in rows))
assert categories=={'component-pad-center':19,'component-pad-edge-hole':4,'component-pad-annulus-only':1,'test-pad-hole':1}
assert sum(r['drill_overlaps_pad']=='True' for r in rows)==24
assert sum(r['drill_overlaps_paste']=='True' for r in rows)==22
assert sum(r['paste_graphics']=='1' for r in rows)==24
assert all(len(r['copper_pad_hits'])==1 and all(p['same_net'] for p in r['copper_pad_hits']) for r in j['observations'])
loguids={r['uuid'] for r in j['observations']}
assert {r['uuid'] for r in j['all_board_via_collisions'] if r['copper_pad_hits'] or r['paste_graphic_hits']}==loguids
cross=json.loads((BASE/'geometry-crosscheck.json').read_text())
assert cross['status']=='pass' and cross['checked_observations']==25
assert collections.Counter(p['attribute'] for p in j['j1']['pads'])=={0:4,1:12,3:2}
assert all(len(p['board_paste_graphics'])==1 and p['board_paste_graphics'][0]['stroke_width_mm']==1.0 for p in j['j1']['pads'] if p['attribute']==0)
sources=json.loads((BASE/'primary-sources.json').read_text())
runtime_checked=[]
assert len(sources['records'])==9
for r in sources['records']:
    assert r['http_status']==200 and r['curl_exit']==0
    assert len(r['review']['quote'].split())<=25
    raw=Path('.issue137-runtime/sources',r['id']+'.html')
    txt=raw.with_suffix('.txt')
    if raw.exists():
        assert sha(raw)==r['sha256']
        assert r['review']['quote'] in re.sub(r'^\d{4} ','',txt.read_text(),flags=re.M)
        runtime_checked.append(r['id'])
assert D(20)*D('.0164')+D('3.58')==D('3.9080')
assert D(20)*D('.016')==D('.3200')
bom=list(csv.DictReader(Path('hardware/kicad/qualification/issue-124-main-bom-pcba/main-bom.csv').open()))
types={cat:{r['lcsc'] for r in bom if cat+' Parts' in r['notes']} for cat in ('Basic','Extended')}
assert len(types['Basic'])==11 and len(types['Extended'])==9
assert D('25.56')-D('8.18')+D('8.21')-D('1.53')+D(20)*D('1.53')-D(9)*D('3.07')==D('27.03')
assert D('91.1050')-D('3.9080')==D('87.1970')
ET.parse(BASE/'geometry-cases.svg')
for target in re.findall(r'\]\(([^)]+)\)',REPORT.read_text()):
    if target.startswith('http'): continue
    file=target.split('#')[0]
    assert (REPORT.parent/file).exists(),target
assert git('rev-parse',COMMIT)==COMMIT
branch=git('branch','--show-current')
assert branch=='issue-137-main-manufacturing-review-prep'
changes=git('diff','--name-status',COMMIT)
for line in changes.splitlines():
    state,path=line.split('\t')
    assert state=='A' and (path==str(REPORT) or path.startswith(str(BASE)+'/')),line
subprocess.run(['git','diff','--check'],check=True)
result=dict(verified_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    base_commit=COMMIT,branch=branch,status='pass',
    categories=categories,board_vias=66,logged_unique_vias=25,
    drill_overlaps_copper=24,drill_overlaps_paste=22,paste_overlap=24,
    geometry_independent_crosscheck='pass',j1=dict(smd=12,pth=4,npth=2,pth_paste_apertures=4),
    primary_sources=9,raw_runtime_hashes_and_quotes_checked=runtime_checked,
    monetary_checks='manual 3.9080; pre-reflow 0.3200 (conditional alternative, not added); Standard setup/stencil/feeders delta 27.03; BOM types 11 Basic + 9 Extended',
    tracked_diff_additions_only=True,design_modified=False,rerouting=False,drc_rerun=False,
    notes='Run using writable isolated GIT_DIR under .issue137-runtime and GIT_WORK_TREE=current repo. Runtime and inherited untracked files excluded from submission.')
(BASE/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
manifest={str(p):sha(p) for p in sorted(BASE.rglob('*')) if p.is_file() and p.name!='manifest.json'}
manifest[str(REPORT)]=sha(REPORT)
(BASE/'manifest.json').write_text(json.dumps(dict(algorithm='sha256',excludes=['manifest.json (self)'],files=manifest),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
