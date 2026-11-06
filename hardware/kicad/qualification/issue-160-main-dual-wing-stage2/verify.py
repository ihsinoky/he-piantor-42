#!/usr/bin/env python3
"""Verify the stopped mechanical-gate deliverable; not PCB qualification."""
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

sys.dont_write_bytecode=True
E=Path(__file__).resolve().parent;R=E.parents[3];T=R/'.issue160-runtime'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(T/'tmp'))
(T/'tmp').mkdir(parents=True,exist_ok=True)
for k in ['CONFIG','CACHE','DATA','STATE']:
    p=T/k.lower();p.mkdir(parents=True,exist_ok=True);env['XDG_'+k+'_HOME']=str(p)
env['PYTHONPATH']=str(R/'.issue129-runtime/kicad/usr/lib/python3/dist-packages')
env['LD_LIBRARY_PATH']=str(R/'.issue129-runtime/kicad/usr/lib/x86_64-linux-gnu')+':'+str(R/'.issue129-runtime/kicad/usr/lib/kicad')
runs=[]
for script in ['mechanical-gate.py','native-readback.py']:
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    result=subprocess.run([sys.executable,str(E/script)],cwd=R,env=env,capture_output=True,text=True,timeout=90)
    (T/(script+'.stdout')).write_text(result.stdout);(T/(script+'.stderr')).write_text(result.stderr)
    assert result.returncode==0,(script,result.stderr)
    if script=='native-readback.py':(E/'native-readback.json').write_text(result.stdout)
    runs.append({'script':script,'start_utc':start,'exit_code':result.returncode})
g=json.loads((E/'mechanical-gate.json').read_text());a,c=g['candidates']
assert a['origin_mm']==[105,81] and c['origin_mm']==[105,73]
assert abs(a['service_to_R2_pad_plus_0p5_mm']-.025)<1e-10
assert a['service_to_H2_driver_d6_mm']==0
assert a['R2_service_gap_after_relative_tolerance_mm'][0]['signed_remaining_mm']<0
assert c['service_to_R2_pad_plus_0p5_mm']>3
# Do not conceal that plan C still fails the larger planar grip scenario.
assert c['side_grasp_projection_sweep'][2]['right_to_H2_head_d4p5_mm']<0
assert all(v==0 for v in g['execution'].values())
assert math.isclose(min(x['minimum_z_above_PCB_screen_mm'] for x in g['cable_bend_height_screen']),10.68,abs_tol=1e-12)
assert math.isclose(max(x['minimum_z_above_PCB_screen_mm'] for x in g['cable_bend_height_screen']),15.8,abs_tol=1e-12)
protected=json.loads(gzip.decompress((E/'protected-start.json.gz').read_bytes()))
changed=[name for name,h in protected.items() if not (R/name).is_file() or digest(R/name)!=h]
assert changed==['docs/decisions.md'],changed
git=['git','--git-dir='+str(T/'git'),'--work-tree='+str(R)]
start=json.loads((E/'start.json').read_text())
original=subprocess.check_output(git+['show',start['base']+':docs/decisions.md'],cwd=R)
decisions=(R/'docs/decisions.md').read_bytes()
assert decisions.startswith(original)
suffix=decisions[len(original):].decode()
assert suffix.count('## D-024 -')==1 and len(re.findall(r'^## ',suffix,re.M))==1
assert hashlib.sha256(original).hexdigest()==protected['docs/decisions.md']
links=[]
for doc in [R/'docs/issue-160-main-dual-wing-stage2.md',E/'README.md']:
    for target in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
        if target.startswith(('https://','http://','#')):continue
        path=target.split('#')[0];assert (doc.parent/path).exists(),(doc,target)
        links.append(path)
allowed=lambda p:p in ['docs/decisions.md','docs/issue-160-main-dual-wing-stage2.md'] or p.startswith(str(E.relative_to(R))+'/')
diff=subprocess.check_output(git+['diff','--name-only',start['base']],cwd=R,text=True).splitlines()
assert all(allowed(p) for p in diff),diff
result={'status':'pass','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'scope':'Preservation, D-024 append and read-only screening only; NOT four-metric board qualification',
 'engineering_outcome':'STOP_PROPOSE_C','protected_files':len(protected),
 'existing_changed_files':changed,'decisions_original_prefix_unchanged':True,
 'unexpected_tracked_changes':[],'local_links_checked':len(links),'runs':runs,
 'new_revision_independent_metrics':{k:None for k in ['required_unconnected','wrong_net_contact','physical_violations','unexplained_transfer_changes']},
 'execution':g['execution'],'order_charge_merge_performed':False}
(E/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('PASS: protected',len(protected),'files; D-024 append only; geometry/native readback; new PCB metrics N/A')
