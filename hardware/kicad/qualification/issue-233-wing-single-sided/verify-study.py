"""Evidence consistency, not design certification. Stdlib-only saved-data check."""
from pathlib import Path
import json,hashlib,csv,gzip,math
E=Path(__file__).resolve().parent;ROOT=E.parents[3]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[];sourcehashes={}
if (E/'verification.json').exists():
 for path,h in read(E/'verification.json')['inputs_sha256'].items():
  target=ROOT/path
  if E not in target.parents:assert sha(target)==h,('pinned production input changed',path)
assert len(read(E/'placement-verification.json'))==4
for row in read(E/'placement-verification.json'):
 w=E/row['variant'];src=E.parent/'issue-200-wing-rev3'/w.name.replace('rev4','rev3');assert sha(src/'input.kicad_pcb')==row['source_sha256'];assert sha(w/'input.kicad_pcb')==row['placement_sha256'];assert row['top_electrical_footprints']==0 and row['purchased_placements']==49 and row['bottom_electrical_footprints']==64
 for k in ('keys_invariant','outline_invariant','mounts_invariant','sensor_and_local_cap_pad_poses_invariant','component_pin_nets_unchanged'):assert row[k]
 q=read(w/'qualification.json');assert sha(w/'main.kicad_pcb')==q['sha256'];d=read(w/'drc.json');assert len(d['unconnected_items'])==q['drc_unconnected'];assert not q['pass'];assert q['width_below_floor']==0 and q['via_pad_below_0p10']==0 and q['min_via_pad_gap_mm']>=.1;assert q['metrics']['wrong_net_contacts']==0 and q['metrics']['unexplained_transfer_changes']==0
 assert read(w/'input.kicad_pro')==read(w/'main.kicad_pro');assert q['all_pads_including_npth']==236
 with gzip.open(w/'via-pad-all-pairs.csv.gz','rt',newline='') as f:
  rs=list(csv.DictReader(f));assert len(rs)==q['via_pad_pairs']==q['all_vias']*236;assert min(float(r['gap_mm']) for r in rs)==q['min_via_pad_gap_mm']
 assert len(d['violations'])==sum(q['drc_types'].values())
 checks.append({'variant':w.name,'DRC_violations':len(d['violations']),'opens':q['drc_unconnected'],'minimum_via_pad_gap_mm':q['min_via_pad_gap_mm'],'design_pass':False})
for row in read(E/'electrical-contract.json'):assert row['logical_errors']==0
main=read(E/'main-unchanged.json');assert sha(ROOT/main['path'])==main['sha256'] and main['F_Cu_footprints']==62 and main['B_Cu_footprints']==0
sourcehashes[main['path']]=main['sha256']
for path,h in read(E/'case/inputs-sha256.json').items():assert sha(ROOT/path)==h,path;sourcehashes[path]=h
for row in read(E/'case/summary.json'):
 assert not row['passed'] and row['exit_floor_clearance_mm']<0 and row['exit_floor_collisions'];assert not row['trial_is_connected_to_GH'];assert row['wall_channel_candidate_valid'] and row['wall_channel_candidate_solids']==1;assert row['wall_channel_candidate_overlap_mm3']<1e-5 and row['floor_0_to_2_removed_mm3']<1e-5
 assert math.isclose(row['trial_length_mm']+row['trial_200mm_excess_mm'],200,abs_tol=1e-9)
 assert not row['post_overlaps']
for pitch in ('16mm','17mm'):
 ps=read(E/'case'/pitch/'post-rescreen.json');assert len(ps)==12 and not any(p['must_move_for_this_trial'] for p in ps);assert min(p['pad_drill_edge_gap_mm'] for p in ps)>=.4
 fly=read(E/'case'/pitch/'fly.json');assert fly['route_geometry_clear'] and not fly['collisions'];assert not fly['stock_170mm_storage_verified'];assert math.isclose(fly['candidate_length_mm']+fly['unstored_excess_mm'],170,abs_tol=1e-9)
assert read(E/'case/verification.json')['saved_STEP_reload_checks_pass']
cost=read(E/'costs.json');assert cost['joints_per_panel']==350 and math.isclose(cost['smt_5panels_usd'],2.8)
for row in cost['rows']:assert all(math.isclose(a/5,b) for a,b in zip(row['batch_cash_usd'],row['per_pair_cash_usd']))
# Pin every production input consumed by the workflow, including source code.
base=E.parent/'issue-200-wing-rev3'
inputs=[ROOT/'docs/decisions.md',ROOT/'docs/issue-183-via-pad-audit.md',ROOT/'hardware/case/issue-230-mount-study/REPORT.md',base/'verify.py',base/'plane-repair.py',E.parent/'issue-129-wing-2layer-routing/evidence/library-pads.json',ROOT/'hardware/jitx/wing/definition.py',base/'panel-17mm/bom.csv',ROOT/'docs/issue-133-wing-cost-check.md']
for w in E.glob('wing-rev4-*'):
 src=base/w.name.replace('rev4','rev3');inputs.extend(src/n for n in ('input.kicad_pcb','input.kicad_pro','definition.json'))
for p in inputs:sourcehashes[str(p.relative_to(ROOT))]=sha(p)
outputs={str(p.relative_to(E)):sha(p) for p in sorted(E.rglob('*')) if p.is_file() and p!=E/'verification.json' and p.suffix not in ('.pyc','.kicad_prl') and '__pycache__' not in p.parts and not p.name.endswith('.lck')}
out={'evidence_consistent':True,'design_qualified':False,'mechanical_qualified':False,'native_ERC_zero_established':False,'procurement_ready':False,'variants':checks,'inputs_sha256':sourcehashes,'study_artifacts_sha256':outputs}
(E/'verification.json').write_text(json.dumps(out,indent=2)+'\n');print('Evidence checks PASS; routing/mechanical qualification remain FAIL')
