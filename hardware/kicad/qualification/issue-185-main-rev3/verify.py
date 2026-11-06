"""Integrity checks on saved independent observations; no regeneration or routing."""
import sys
sys.dont_write_bytecode=True
from common import *
import csv,subprocess,re,ast
read=lambda name:json.loads((E/name).read_text())
a=read('inspection/final/assessment.json');g=read('inspection/final/connectivity.json');d=read('inspection/final/transfer-diff.json');board=E/'inspection/final/main.kicad_pcb';h=digest(board)
assert a['pass_acceptance'] and all(v==0 for v in a['metrics'].values()) and a['measured_unconnected']==0
assert g['nets_checked']==44 and sum(n['required_pad_count'] for n in g['nets'])==221 and g['required_unconnected']==g['wrong_net_contacts']==0
assert d['output_sha256']==h and d['input_sha256']=='acab039f3b5f5ea30500d2f8537e320e198f881c227a3c3042753fc021c30f1c'
assert not d['nonroute_removed'] and not d['nonroute_added'] and not d['route_delta_failures']
assert (d['baseline_vias'],d['final_vias'],d['explained_via_moves'],d['retained_segments'],d['new_segments'])==(113,113,35,693,94)
old=E.parent/'issue-175-main-dual-wing-final2'
assert read('circuit-check-final.json')['pass_check'] and read('circuit-check-final.json')['logical_pins_checked']==245 and read('circuit-check-final.json')['PCB_sha256']==h
assert digest(E/'inspection/final/main.kicad_pro')==digest(old/'inputs/final/main.kicad_pro')
assert digest(E/'local35/main.kicad_pcb')==h
s=read('local35/audit/via-pad/summary.json');rows=read('local35/audit/via-pad/all-vias.json')
assert s['source_sha256']==h and s['total_vias']==113 and s['violates_0p10']==0 and s['min_annulus_gap_mm']>=.1
assert len(rows)==113 and all(r['passes_0p10'] and r['min_annulus_gap_mm']>=.1 and r['classification']=='none' for r in rows)
with (E/'local35/audit/via-pad/all-vias.csv').open() as f:assert len(list(csv.DictReader(f)))==113
s33=read('straight33/audit/via-pad/summary.json');assert s33['violates_0p10']==2
changes=read('straight33/changes.json')+read('local35/changes.json');assert len(changes)==len({r['via_uuid'] for r in changes})==35
probes=read('source183/move-probes.json');assert {r['via_uuid'] for r in probes}=={r['via_uuid'] for r in changes}
assert {r['via_uuid'] for r in read('local35/changes.json')}=={r['via_uuid'] for r in probes if r['straight_stub_candidate_mm'] is None}
paste=read('paste-via-check.json');assert paste['board_sha256']==h and paste['vias_checked']==113 and paste['via_copper_overlaps_paste']==paste['drill_overlaps_paste']==0
geometry=read('geometry-check.json');assert geometry['board_sha256']==h and geometry['pass_check'] and geometry['all_66_footprint_placements_identical']
r=read('resistance-summary.json')['rows'][0];assert r['board_sha256']==h and r['all_loop_targets_met_in_model'] and r['rail_common_loop_ohm']<=.05 and all(x<=.05 for x in r['branch_loop_ohm'].values())
assert read('power-extraction-final.json')['PCB_sha256']==h and read('ground-extraction-final.json')['board_sha256']==h
assert len(read('ground-extraction-final.json')['rows'])==4 and read('ground-model-verification.json')['pass_numerics']
cam=read('cam-check.json');assert cam['source_sha256']==h and cam['pass_check'] and cam['plane_symmetric_difference_mm2']==0 and cam['pth_round_vias']==113
for row in cam['archive_members']:assert digest(E/'manufacturing/gerber'/row['name'])==row['sha256']
assert digest(E/'manufacturing/main-stage2-fabrication-review.zip')==cam['archive_sha256']
assert read('export-provenance.json')['board_sha256']==h
for name in ['BOM.csv','CPL.csv']:
 with (E/'manufacturing'/name).open() as f:assert len(list(csv.DictReader(f)))==58
assert (E/'manufacturing/BOM.csv').read_bytes()==(old/'manufacturing/BOM.csv').read_bytes()
assert (E/'manufacturing/CPL.csv').read_bytes()==(old/'manufacturing/CPL.csv').read_bytes()
prov=read('source183/provenance.json')
for name,expected in prov['source_files_sha256'].items():assert digest(E/'source183'/Path(name).name)==expected
# Existing inputs and earlier deliverables are immutable, apart from appending D-030.
G=['git','--git-dir='+str(T/'git'),'--work-tree='+str(R)]
changed=subprocess.check_output(G+['diff','--name-only','dcf5c61d9b8480da9698f71c5209d516d6231898','--'],text=True).splitlines();allowed=str(E.relative_to(R))+'/'
assert all(f.startswith(allowed) or f in ['docs/decisions.md','docs/issue-185-main-rev3.md'] for f in changed),changed
original=subprocess.check_output(G+['show','dcf5c61d9b8480da9698f71c5209d516d6231898:docs/decisions.md'])
decisions=(R/'docs/decisions.md').read_bytes();assert decisions.startswith(original) and decisions.count(b'## D-030 -')==1
assert b'## D-028' not in decisions[len(original):] and b'## D-029' not in decisions[len(original):]
links=0
for f in [R/'docs/issue-185-main-rev3.md',E/'README.md']:
 for target in re.findall(r'\]\(([^)]+)\)',f.read_text()):
  if target.startswith(('http://','https://','#')):continue
  assert (f.parent/target.split('#')[0]).exists(),(f,target);links+=1
for f in E.glob('*.py'):ast.parse(f.read_text())
manifest=read('manifest.json')
for name,expected in manifest.items():assert digest(E/name)==expected,(name,'manifest mismatch')
save(E/'verification.json',dict(utc=now(),pass_verification=True,board_sha256=h,four_metrics=a['metrics'],nets_checked=44,logical_pins_checked=245,required_copper_pads_checked=221,all_vias_checked=113,min_pad_gap_mm=s['min_annulus_gap_mm'],model_targets_pass=True,CAM_pass=True,unchanged_existing_segments=693,planned_moves=35,global_routes=0,local_links_checked=links,manifest_files=len(manifest),BOM_CPL_byte_identical_to_Rev2=True,manufacturing_GO=False,visual_review='CAM contact sheet viewed: four copper layers, GND plane reservations, north C26-C28 paste, bottom USB shell paste.',orders=0,charges=0,merges=0))
print('PASS: all44 nets / four zeros / all113 gaps / resistance / CAM / provenance / scope')
