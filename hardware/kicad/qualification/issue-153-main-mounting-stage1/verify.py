"""Verify report evidence and optional task-start preservation snapshot.

Stdlib only by default. --native also reruns the KiCad effective-shape check.
JSON on stdout. Does not write or modify design files.
"""
from pathlib import Path
import argparse
import csv
import datetime
import hashlib
import json
import os
import math
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import measure

parser=argparse.ArgumentParser()
parser.add_argument('--native',action='store_true')
parser.add_argument('--task-finalization',action='store_true',help='Enforce the one-hour finish-task timebox; requires --task-start-utc')
parser.add_argument('--task-start-utc',help='ISO8601 start of the finish task, with UTC offset')
args=parser.parse_args()
E=Path(__file__).resolve().parent
ROOT=measure.ROOT
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
inputs=json.loads((E/'inputs.json').read_text())
context_paths={'docs/issue-150-case-stage1.md','hardware/case/issue-150-stage1/measurements.json'}
unavailable_context=[p for p in inputs['files'] if not (ROOT/p).exists() and p in context_paths]
bad=[p for p,h in inputs['files'].items() if p not in unavailable_context and (not (ROOT/p).is_file() or sha(ROOT/p)!=h)]
assert not bad,bad
reproduced=subprocess.check_output([sys.executable,str(E/'measure.py')],env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
assert reproduced==(E/'measurements.json').read_bytes(),'measurement JSON differs'
m=json.loads(reproduced)
n=json.loads((E/'native-crosscheck.json').read_text())
assert n['status']=='pass' and n['board_sha256']==m['input']['sha256']
assert n['candidates_checked']==len(m['survey']['candidates'])==19
assert n['all_pad_positions_sizes_orientations_checked']==199
assert n['existing_drills_checked']==72 and n['courtyard_polygons_checked']==40
for row,native in zip(m['survey']['candidates'],n['rows']):
    assert row['label']==native['label'] and row['xy']==native['xy_mm']
    for key,group in row['groups'].items():
        ng=native['groups'][key]
        assert abs(ng['keepout_gap_mm']-group['keepout_gap'])<=.000002
        assert set(ng['keepout_hit_uuids'])=={h['item']['uuid'] for h in group['keepout_hits']}
    ext=row['label'].startswith('extension-')
    assert all(z['disk_5mm_hits_existing_fill']!=ext and z['drill_2_2mm_hits_existing_fill']!=ext for z in native['zones'])
native_reproduced=False
if args.native:
    native_bytes=subprocess.check_output([sys.executable,str(E/'native-check.py')],env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    assert native_bytes==(E/'native-crosscheck.json').read_bytes(),'native JSON differs'
    native_reproduced=True
affected=list(csv.DictReader((E/'affected-copper.csv').open()))
assert len(affected)==3 and {r['net'] for r in affected}=={'VBUS','GND','WING_EN'}
assert all(r['kind']=='track' and r['width']=='0.1' for r in affected)
plans=json.loads((E/'plans.json').read_text())
assert plans['A-retain-4']['holes']==[[79,92],[121,81],[79,119],[102,111.5]]
assert set(plans['A-retain-4']['affected_existing_items'])=={r['uuid'] for r in affected}
assert not plans['A-retain-4']['affected_old_25_POFV_vias']
assert not plans['A0-retain-3']['affected_existing_items'] and not plans['B-extend-4']['affected_existing_items']
assert plans['B-extend-4']['outline']==[70,78,130,122]
lookup={r['label']:r for r in m['survey']['candidates']}
for name in ['W-upper','NE-corner','SW-corner','S-proposed']:
    assert lookup[name]['provisional_body_clear']
    assert not lookup[name]['groups']['pads']['keepout_hits']
    assert not lookup[name]['groups']['vias']['keepout_hits']
    assert all(not g['hole_hits'] for g in lookup[name]['groups'].values())
independent=json.loads((ROOT/'hardware/kicad/qualification/issue-121-full-auto-conditions/evidence/inspection/main-cell1/krt/independent.json').read_text())
assert independent['pass_acceptance'] and set(independent['metrics'].values())=={0}
# Rebuild all derived assets in task-local scratch, then compare every byte.
scratch=ROOT/'.issue153-runtime/tmp'
scratch.mkdir(parents=True,exist_ok=True)
asset_names=['affected-copper.csv','candidates.csv','plans.json','inputs.json',
             'retained-outline.svg','extended-outline.svg','survey-map.svg']
with tempfile.TemporaryDirectory(dir=scratch) as tmp:
    subprocess.check_output([sys.executable,str(E/'build-assets.py'),'--output-dir',tmp],
        env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    for name in asset_names:
        assert (Path(tmp)/name).read_bytes()==(E/name).read_bytes(),name
for row in m['survey']['candidates']:
    assert row['local_xy']==[row['xy'][0]-row['outline'][0],row['xy'][1]-row['outline'][1]]

# Check rendered geometry, including hole diameters and highlighted trace endpoints.
ns={'s':'http://www.w3.org/2000/svg'}
for filename,plan in [('retained-outline.svg','A-retain-4'),('extended-outline.svg','B-extend-4')]:
    svg=ET.parse(E/filename).getroot()
    outline=plans[plan]['outline']
    def unscale(x,y): return [(float(x)-85)/12+outline[0],(float(y)-95)/12+outline[1]]
    for radius in [13.2,30]:
        circles=[c for c in svg.findall('s:circle',ns) if float(c.get('r'))==radius and c.get('stroke')=='#18764c']
        assert len(circles)==4
        assert [unscale(c.get('cx'),c.get('cy')) for c in circles]==plans[plan]['holes']
    labels=[''.join(t.itertext()) for t in svg.findall('s:text',ns)]
    for i,(x,y) in enumerate(plans[plan]['holes'],1):
        assert f'H{i} ({x:g}, {y:g})' in labels
    assert f'{outline[2]-outline[0]:g} mm (X {outline[0]:g} to {outline[2]:g})' in labels
    assert '44 mm (Y 78 to 122)' in labels
    red=[l for l in svg.findall('s:line',ns) if l.get('stroke')=='#d2203d']
    expected=[r for r in affected if r['plan']==plan]
    assert len(red)==len(expected)
    for line,row in zip(red,expected):
        for actual,target in [(unscale(line.get('x1'),line.get('y1')),[float(row['start_x']),float(row['start_y'])]),
                              (unscale(line.get('x2'),line.get('y2')),[float(row['end_x']),float(row['end_y'])])]:
            assert all(math.isclose(a,b,rel_tol=0,abs_tol=1e-9) for a,b in zip(actual,target)),(actual,target)
ET.parse(E/'survey-map.svg')

# Compare all numerical cells of both plan-A dimension tables with raw measurements.
report=(ROOT/'docs/issue-153-main-mounting-stage1.md').read_text()
hole_rows=[l for l in report.splitlines() if l.startswith('| H') and not l.startswith('| H1 | VBUS') and not l.startswith('| H4 | WING_EN') and not l.startswith('| H4 | GND')]
assert len(hole_rows)==8
selected=[lookup[n] for n in ['W-upper','NE-corner','SW-corner','S-proposed']]
for line,row in zip(hole_rows[:4],selected):
    cells=[c.strip() for c in line.strip('|').split('|')]
    assert list(map(float,cells[1].split(',')))==row['xy']
    assert list(map(float,cells[2].split(',')))==row['local_xy']
    assert list(map(float,cells[3:]))==[round(row[k],2) for k in ['edge_center_distance','hole_edge_ligament','keepout_to_edge','head_4_5_to_edge']]
for line,row in zip(hole_rows[4:],selected):
    cells=[c.strip() for c in line.strip('|').split('|')][1:]
    actual=[float(re.search(r'[+−-]?\d+\.\d+',c.replace('−','-')).group()) for c in cells]
    expected=[row['groups'][k]['keepout_gap'] for k in ['pads','tracks','vias']]
    expected += [row['actual_courtyard_nearest']['keepout_gap'],row['body_reservation_nearest']['keepout_gap'],row['nearest_existing_drill']['proposed_drill_edge_gap']]
    assert actual==[round(v,3) for v in expected],(actual,expected)
extension=[lookup[n] for n in ['extension-NW','extension-NE','extension-SW','extension-SE']]
assert [round(min(r['groups'][k]['keepout_gap'] for r in extension),3) for k in ['pads','tracks','vias']]==[4.025,5.080,7.736]
assert all(r['provisional_body_clear'] and r['pad_track_via_clear'] for r in extension)
assert math.isclose(60*44/(48*44)-1,.25)
snapshot=ROOT/'.issue153-runtime/before-hashes.json'
preservation=dict(status='not available outside original task runtime')
if snapshot.exists():
    before=json.loads(snapshot.read_text())
    missing=[p for p in before if not (ROOT/p).is_file()]
    changed=[p for p,h in before.items() if (ROOT/p).is_file() and sha(ROOT/p)!=h]
    assert not missing and not changed,(missing,changed)
    preservation=dict(status='pass',checked_files=len(before),missing=missing,changed=changed,
        scope='All tracked files and pre-existing untracked #147/#149/#150 report/evidence files; existing runtime contents excluded.')
now=datetime.datetime.now(datetime.timezone.utc)
start=datetime.datetime.fromisoformat(args.task_start_utc) if args.task_start_utc else None
if start:
    assert start.tzinfo is not None and start.utcoffset()==datetime.timedelta(0),'UTC offset required'
elapsed=(now-start).total_seconds() if start else None
if args.task_finalization:
    assert elapsed is not None and 0<=elapsed<3600,'Finish-task verification exceeded one-hour timebox or start missing'
print(json.dumps(dict(status='pass',utc=now.isoformat(),finish_task_start_utc=start.isoformat() if start else None,
    elapsed_seconds=elapsed,timebox_seconds=3600,finish_timebox_enforced=args.task_finalization,
    input_hashes_checked=len(inputs['files'])-len(unavailable_context),unavailable_context_inputs=unavailable_context,
    measurement_json_byte_reproduced=True,native_json_byte_reproduced=native_reproduced,
    native_candidate_comparison='pass',native_distance_tolerance_mm=.000002,
    original_121_independent_metrics=independent['metrics'],
    scan_points=m['survey']['scan']['total_lattice_points'],
    component_screened_points=m['survey']['scan']['component_screened_points'],
    pad_track_via_clear_points=m['survey']['scan']['clear_points'],
    plan_A_affected_tracks=3,plan_A_affected_pads=0,plan_A_affected_vias=0,
    plan_A_existing_25_POFV_affected=0,svg_xml_checked=3,derived_asset_files_byte_reproduced=len(asset_names),
    svg_hole_centers_diameters_labels_and_affected_traces='pass',report_plan_A_dimension_tables='pass',
    plan_B_nonplane_and_body_clearance='pass',existing_file_preservation=preservation,
    routing_runs=0,zone_refill_runs=0,pcb_save_calls=0,new_DRC_runs=0,
    limitation='Nominal geometry and reproducibility only. No new routing, 3D interference, mechanical load, manufacturing or electrical qualification claimed.'),ensure_ascii=False,indent=2))
