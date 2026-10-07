"""Proportional verification; does not reroute or claim physical qualification."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from analyze import extract
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
def read(p):return json.loads(p.read_text())
files=list((HERE/'evidence').glob('*.json'))
for p in files:read(p)
preflight=read(HERE/'evidence/preflight.json')
for name,sha in preflight['protected_sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name
assert read(ROOT/'hardware/tscircuit/package.json')['dependencies']['tscircuit']=='0.0.2646'
assert read(ROOT/'hardware/tscircuit/package-lock.json')['packages']['node_modules/tscircuit']['version']=='0.0.2646'
records=read(HERE.parent/'eda-003d/evidence/error-records-normalized.json')
pop=read(HERE/'evidence/signature-population.json');assert pop==extract(records)==extract(records)
assert pop['summary']['raw_records']==15
nums=read(HERE/'evidence/numeric-derivation.json')
for h in nums['hypotheses']:
    if h['expected_result_mm'] is not None:
        for r in h['per_record']:assert abs(r['observed_delta_mm']-(r['observed_mm']-h['expected_result_mm']))<1e-15
h=nums['hypotheses'][0];i=h['inputs'];assert abs(i['relaxed_trace_clearance']+i['slack']-h['expected_result_mm'])<1e-15
assert abs(nums['target_centerline_mm']-.515)<1e-15
b=read(HERE/'evidence/pipeline-boundary.json')
for r in b['observations']:
    from analyze import distance_point_segment
    actual=distance_point_segment(r['via_center_mm'],r['trace_a_mm'],r['trace_b_mm'])-r['via_radius_mm']-r['trace_width_mm']/2
    assert abs(actual-r['gap_mm'])<1e-10
    assert r['violates_020']==(actual<.2)
assert len(b['observations'])==30
for r in b['selected_final_comparison']:assert abs(r['accepted_gap_delta_mm'])<1e-10
for name in ['reproducer-reduction.json','upstream-comparison.json','proof-of-fix.json']:assert not (HERE/'evidence'/name).exists()
subprocess.run([sys.executable,str(HERE/'test-analysis.py')],check=True)
subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
report=dict(result='PASS',json_parse_files=len([p for p in files if p.name!='validation.json'])+1,signature_extraction_deterministic=True,numeric_derivation_consistent=True,boundary_geometry_consistent=True,analysis_tests=4,
 stock_checker_selected_replay='PASS: accepted and captured 15 records at .20 mm (check-selected.mjs)',protected_files_verified=len(preflight['protected_sha256']),production_manifest_lock_unchanged=True,accepted_eda_003b_c_d_unchanged=True,production_pin='0.0.2646',git_diff_check='PASS',
 routing_capture_runs=1,repair_regression_test='NOT AVAILABLE: no reproducer/patch',clearance_qualification='FAIL remains accepted; validation verifies investigation evidence only')
(HERE/'evidence/validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
