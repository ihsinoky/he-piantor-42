#!/usr/bin/env python3
"""Recompute stopped-gate evidence and check preservation, not PCB qualification."""
from pathlib import Path
import datetime
import gzip
import hashlib
import json
import math
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
E = Path(__file__).resolve().parent
R = E.parents[3]
T = R / '.issue163-runtime'
B = R / '.issue129-runtime'
GIT = ['git', '--git-dir='+str(T/'git'), '--work-tree='+str(R)]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(name, x):
    (E/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')

env = {k:v for k,v in os.environ.items() if k not in ['DISPLAY','WAYLAND_DISPLAY']}
env.update(PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(T/'tmp'),
           PYTHONPATH=str(B/'kicad/usr/lib/python3/dist-packages'),
           LD_LIBRARY_PATH=str(B/'kicad/usr/lib/x86_64-linux-gnu')+':'+str(B/'kicad/usr/lib/kicad'))
for kind in ['CONFIG','CACHE','DATA','STATE']:
    p=T/kind.lower()
    p.mkdir(exist_ok=True,parents=True)
    env['XDG_'+kind+'_HOME']=str(p)
(T/'tmp').mkdir(exist_ok=True)
runs = []
for name,script in [('mechanical-and-power-preflight',E/'analyze.py'),
                    ('draw-review-projections',E/'draw.py'),
                    ('original-native-readback',E.parent/'issue-160-main-dual-wing-stage2/native-readback.py')]:
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    proc=subprocess.run([sys.executable,str(script)],cwd=R,env=env,capture_output=True,text=True,timeout=120)
    folder=E/'processes'/name
    folder.mkdir(parents=True,exist_ok=True)
    (folder/'stdout').write_text(proc.stdout)
    (folder/'stderr').write_text(proc.stderr)
    record=dict(argv=[sys.executable,str(script.relative_to(R))],start_utc=start,
                end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                exit_code=proc.returncode,timeout_seconds=120,
                runtime='.issue163-runtime',scope='Read-only original-board check; no new-board qualification')
    (folder/'record.json').write_text(json.dumps(record,indent=2)+'\n')
    assert proc.returncode==0,(name,proc.stderr)
    if name=='original-native-readback':
        save('native-readback.json',json.loads(proc.stdout))
    runs.append(record)

start=json.loads((E/'start.json').read_text())
assert subprocess.check_output(GIT+['branch','--show-current'],text=True).strip()==start['branch']
base=subprocess.check_output(GIT+['show',start['base']+':docs/decisions.md'])
prior=subprocess.check_output(GIT+['show',start['pr162_head']+':docs/decisions.md'])
current=(R/'docs/decisions.md').read_bytes()
assert prior.startswith(base) and current.startswith(prior)
suffix=current[len(prior):].decode()
assert suffix.count('## D-025 -')==1 and len(re.findall(r'^## ',suffix,re.M))==1

paths=subprocess.check_output(GIT+['diff-tree','--no-commit-id','--name-only','-r',
                                    start['base'],start['pr162_head']],text=True).splitlines()
imports=[]
for name in paths:
    original=subprocess.check_output(GIT+['show',start['pr162_head']+':'+name])
    actual=(R/name).read_bytes()
    assert (actual.startswith(original) if name=='docs/decisions.md' else actual==original),name
    imports.append(dict(path=name,pr162_sha256=hashlib.sha256(original).hexdigest(),
                        exact_match=(actual==original),allowed_D025_append=(name=='docs/decisions.md')))
assert len(imports)==27
save('import-proof.json',dict(source_commit=start['pr162_head'],files=imports,
                               all_imported_contents_unchanged=True,D025_append_only=True))

protected=json.loads(gzip.decompress((E/'protected-start.json.gz').read_bytes()))
changed=[p for p,h in protected.items() if not (R/p).is_file() or sha(R/p)!=h]
assert not changed,changed
inputs=json.loads((E/'input-hashes.json').read_text())
assert all(sha(R/p)==h for p,h in inputs.items())
mechanical=json.loads((E/'mechanical.json').read_text())
assert mechanical['outcome']=='STOP_MECHANICAL_GATE_UNESTABLISHED'
assert all(x==0 for x in mechanical['execution'].values())
assert mechanical['overhang']['actual_force_N'] is None
assert mechanical['overhang']['verified_board_deflection_mm'] is None
assert mechanical['adopted_geometry']['J3_origin_mm']==[105.,73.]
assert math.isclose(mechanical['overhang']['body_center_outside_support_polygon_mm'],9.543587637085826,abs_tol=1e-10)
assert mechanical['projections']['H2_to_service_driver_d4_gap_mm']>1.6

# Cross-check the fresh #141-based ideal-Main calculation against the historical
# #157 result. This establishes model consistency, not a routed-board voltage.
import csv
rows=list(csv.DictReader((E/'ideal-main-dc.csv').open()))
old=json.loads((E.parent/'issue-157-main-dual-wing-stage1/power-model.json').read_text())
labels={'component-5mA':'component','planning-127mA':'planning127mA',
        'envelope-11mA':'envelope','envelope-allowance-278mA':'allowance278mA'}
checked=0
for prior_row in old['summary']:
    matches=[p for p in rows if p['load_case']==labels[prior_row['load_case']]
             and float(p['pitch_mm'])==prior_row['pitch_mm']
             and float(p['temperature_C'])==prior_row['temperature_C']
             and float(p['width_factor'])==prior_row['width_factor']
             and float(p['source_at_U5_V'])==4.75 and float(p['contact_each_ohm'])==.05]
    assert len(matches)==1
    assert math.isclose(float(matches[0]['ideal_Main_sensor_voltage_V']),
                        prior_row['local_at_source_4V75_V'],abs_tol=1e-12)
    checked+=1

allowed=lambda p:p=='docs/decisions.md' or p=='docs/issue-160-main-dual-wing-stage2.md' or p=='docs/issue-163-main-dual-wing-plan-c.md' or p.startswith('hardware/kicad/qualification/issue-160-main-dual-wing-stage2/') or p.startswith(str(E.relative_to(R))+'/')
diff=subprocess.check_output(GIT+['diff','--name-only',start['base']],text=True).splitlines()
assert all(allowed(p) for p in diff),diff
links=0
for doc in [R/'docs/issue-163-main-dual-wing-plan-c.md',E/'README.md']:
    if not doc.exists():continue
    for dest in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
        if dest.startswith(('https://','http://','#')):continue
        assert (doc.parent/dest.split('#')[0]).exists(),(doc,dest)
        links+=1

result=dict(status='pass',checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            scope='Artifact/preservation/model checks only; mechanical gate remains unestablished',
            engineering_outcome=mechanical['outcome'],protected_files=len(protected),
            existing_changed_files=changed,PR162_imported_files=len(imports),
            D024_byte_preserved=True,D025_only_append=True,
            original_input_hashes_match=True,ideal_main_model_crosschecked_cases=checked,
            local_links_checked=links,runs=runs,execution=mechanical['execution'],
            new_board_independent_metrics={k:None for k in ['required_unconnected','wrong_net_contact','physical_violations','unexplained_transfer_changes']},
            order_charge_merge_performed=False)
save('verification.json',result)
print(json.dumps({k:result[k] for k in ['status','engineering_outcome','protected_files',
                                      'PR162_imported_files','ideal_main_model_crosschecked_cases']},indent=2))
