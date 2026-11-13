"""Read-only saved-evidence consistency audit; never substitutes for design gates."""
from pathlib import Path
import json,hashlib,re
E=Path(__file__).resolve().parent;ROOT=E.parents[3];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
manifest=read(E/'evidence-manifest.json')
for path,digest in manifest['artifact_sha256'].items():assert sha(E/path)==digest,('artifact changed',path)
for path,digest in manifest['input_sha256'].items():assert sha(ROOT/path)==digest,('input changed',path)
# Independently parse the copied front-native footprint. Contract rows use Y-up.
source=(E/'connector/JST_GH_SM14B-GHS-TB_1x14-1MP_P1.25mm_Horizontal.kicad_mod').read_text()
rows=[dict(number=n,x_mm=float(x),y_mm=-float(y)) for n,x,y in re.findall(r'\(pad (\S+) smd roundrect \(at ([\d.-]+) ([\d.-]+)\)',source)]
assert rows==read(E/'connector/pads.json') and len(rows)==16
contracts={r['variant']:r for r in read(E/'electrical-contract.json')};cases={r['variant']:r for r in read(E/'case/summary.json')};qs=[]
for w in sorted(E.glob('wing-rev4-*')):
 q=read(w/'qualification.json');assert q['sha256']==sha(w/'main.kicad_pcb');assert q['width_below_floor']==q['via_pad_below_0p10']==0
 d=read(w/'drc.json');assert q['drc_unconnected']==len(d['unconnected_items']) and sum(q['drc_types'].values())==len(d['violations'])
 m=q['metrics'];expected=not d['violations'] and not d['unconnected_items'] and all(v==0 for v in m.values());assert q['pass']==expected
 assert contracts[w.name]['logical_errors']==0
 if q['pass']:
  r=read(w/'resistance-extraction.json');assert r['board_sha256']==q['sha256'] and len(r['rows'])==8
  for row in r['rows']:assert abs(sum(row['result_at_20C']['load_A'].values())-.127)<1e-12 and row['result_at_20C']['kcl_residual_A']<1e-6
 qs.append(q)
assert read(E/'case/verification.json')['saved_STEP_checks_pass']
assert all(r['native_transformed_probes_pass'] for r in read(E/'connector/placement.json'))
for r in cases.values():
 assert r['trial_is_connected_to_GH'] and r['gh_reserved_floor_gap_mm']>=.5 and r['wall_channel_candidate_valid'] and r['wall_channel_candidate_solids']==1 and r['wall_channel_candidate_overlap_mm3']<1e-5 and r['floor_0_to_2_removed_mm3']<1e-6 and not r['post_overlaps']
for path in (E/'case').glob('*/post-rescreen.json'):assert not any(r['must_move_for_this_trial'] for r in read(path))
assert all(r['pass_body_overlap_screen'] for r in read(E/'body-clearance.json'))
power=read(E/'power-summary.json');assert {r['board'] for r in power['boards']}=={r['board'] for r in qs if r['pass']};assert not power['adopted_200mm_below_4p60']
main=read(E/'main-unchanged.json');assert main['F_Cu_footprints']==62 and main['B_Cu_footprints']==0 and sha(ROOT/main['path'])==main['sha256']
result={'evidence_consistency_pass':True,'artifacts_checked':len(manifest['artifact_sha256']),'inputs_checked':len(manifest['input_sha256']),'routing_passes':[q['board'] for q in qs if q['pass']],'routing_failures':[q['board'] for q in qs if not q['pass']],'all_four_routing_qualified':all(q['pass'] for q in qs),'original_case_route_pass':False,'case_proposal_saved_STEP_replay_pass':True,'complete_harness_tolerance_certified':False,'production_inputs_unchanged':True,'manufacturing_release':False}
(E/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
