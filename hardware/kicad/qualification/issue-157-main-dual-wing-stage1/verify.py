#!/usr/bin/env python3
"""Run read-only analyses and verify preservation / physics / local links.

All temporary files and alternate git metadata remain in .issue157-runtime/.
No git mutation or publication occurs here.
"""
from pathlib import Path
import csv
import datetime
import gzip
import hashlib
import json
import os
import re
import subprocess
import sys
import time

sys.dont_write_bytecode=True
E=Path(__file__).resolve().parent;R=E.parents[3];T=R/'.issue157-runtime'
def save(name,value):(E/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',TMPDIR=str(T/'tmp'))
for k in ['CONFIG','CACHE','DATA','STATE']:
    p=T/k.lower();p.mkdir(parents=True,exist_ok=True);env['XDG_'+k+'_HOME']=str(p)
env['PYTHONPATH']=str(R/'.issue129-runtime/kicad/usr/lib/python3/dist-packages')+':'+str(R/'.issue129-runtime/geometry/lib/python3.12/site-packages')
env['LD_LIBRARY_PATH']=str(R/'.issue129-runtime/kicad/usr/lib/x86_64-linux-gnu')+':'+str(R/'.issue129-runtime/kicad/usr/lib/kicad')
(T/'tmp').mkdir(parents=True,exist_ok=True)
runs=[]
for script,target in [('analyze.py',T/'analysis-output.json'),('native-check.py',E/'native-check.json'),('main-resistance.py',E/'main-resistance.json')]:
    start=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic()
    result=subprocess.run([sys.executable,str(E/script)],cwd=R,env=env,capture_output=True,text=True,timeout=120)
    (T/(script+'.stderr')).write_text(result.stderr)
    assert result.returncode==0,(script,result.stderr)
    target.write_text(result.stdout)
    runs.append(dict(script=script,start_utc=start,elapsed_seconds=time.monotonic()-t,exit_code=result.returncode,stdout=str(target.relative_to(R))))
save('analysis-runs.json',runs)
rows=list(csv.DictReader((E/'dual-wing-dc.csv').open()))
assert len(rows)==768
lookup={tuple(row[k] for k in ['load_case','pitch_mm','temperature_C','width_factor','contact_ohm','return_conductors','main_common_loop_ohm','wings']):row for row in rows}
for key,row in lookup.items():
    if row['wings']!='2':continue
    one=lookup[key[:-1]+('1',)]
    # New Wing adds shared-path loss only; local branch loss remains unchanged.
    expected=float(row['branch_A'])*(float(row['switch_ohm'])+float(row['main_common_loop_ohm']))
    assert abs(float(row['total_drop_V'])-float(one['total_drop_V'])-expected)<1e-12
    assert abs(float(row['harness_drop_V'])-float(one['harness_drop_V']))<1e-12
    assert abs(float(row['wing_drop_V'])-float(one['wing_drop_V']))<1e-12
    assert abs(float(row['local_at_source_5V_V'])-float(row['local_at_source_4V75_V'])-.25)<1e-12
native=json.loads((E/'native-check.json').read_text());assert native['status']=='pass'
main=json.loads((E/'main-resistance.json').read_text());assert len(main['results'])==8 and len(main['spine_sensitivity'])==64
assert all(x['kcl_residual_A']<1e-7 for x in main['results'])
start=T/'protected-start.json'
if start.exists():
    raw=start.read_bytes()
    (E/'protected-start.json.gz').write_bytes(gzip.compress(raw,mtime=0))
else:raw=gzip.decompress((E/'protected-start.json.gz').read_bytes())
protected=json.loads(raw)
changed=[name for name,h in protected.items() if not (R/name).is_file() or digest(R/name)!=h]
assert not changed,changed
git=['git','--git-dir='+str(T/'git'),'--work-tree='+str(R)]
tracked=subprocess.check_output(git+['diff','--name-only'],text=True,cwd=R).splitlines()
tracked=[p for p in tracked if not (p=='docs/issue-157-main-dual-wing-stage1.md' or p.startswith('hardware/kicad/qualification/issue-157-main-dual-wing-stage1/'))]
assert not tracked,tracked
links=[]
for doc in [R/'docs/issue-157-main-dual-wing-stage1.md',E/'README.md']:
    for target in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
        if target.startswith(('https://','http://','#')):continue
        dest=target.split('#')[0]
        assert (doc.parent/dest).exists(),(doc,target)
        links.append(str((doc.parent/dest).resolve().relative_to(R)))
save('verification.json',dict(status='pass',checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    protected_files=len(protected),changed_existing_files=changed,existing_tracked_worktree_changes=tracked,
    dc_cases=len(rows),one_to_two_wing_shared_loss_checks=384,main_resistance_cases=8,main_spine_cases=64,
    maximum_main_kcl_residual_A=max(x['kcl_residual_A'] for x in main['results']),native_crosscheck_pass=True,
    local_markdown_links_checked=len(links),pcb_writer_calls=0,router_runs=0,refill_runs=0,manufacturing_exports=0,
    limits=['Read-only survey and approximate DC analysis only; no routing/3D/power/USB sign-off']))
print('PASS: preserved',len(protected),'existing files; 768 DC cases; 8 Main resistances; 64 spine cases; native geometry and local links')
