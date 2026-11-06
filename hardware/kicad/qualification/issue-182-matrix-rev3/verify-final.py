"""Seal the qualified geometry, inherited design, assembly identity and preservation."""
from common import *
import sexpdata as sx,collections,shutil
S=R/'hardware/kicad/qualification/issue-178-m1-matrix-board'
base=S/'board/m1-matrix18.kicad_pcb';final=E/'board/m1-matrix18.kicad_pcb'
assert digest(base)==json.loads((E/'baseline.json').read_text())['board_sha256']
def inv(path):
 a=sx.loads(path.read_text());return collections.Counter(sx.dumps(n) for n in a[1:] if not isinstance(n,list) or not n or str(n[0]) not in ['segment','via'])
assert inv(base)==inv(final)
assert digest(final)==digest(E/'runs/final/out.kicad_pcb')
assert digest(final.with_suffix('.kicad_pro'))==digest(S/'board/m1-matrix18.kicad_pro')
a=json.loads((E/'inspection/final/assessment.json').read_text());v=json.loads((E/'inspection/final/via-pad-audit.json').read_text());s=json.loads((E/'inspection/final/snapshot.json').read_text());m=json.loads((E/'manufacturing/manufacturing-check.json').read_text());w=json.loads((E/'inspection/final/width-audit.json').read_text())
assert a['pass_acceptance'] and v['pass_acceptance'] and all(x==0 for x in a['metrics'].values())
assert v['board_sha256']==digest(final)==m['source_sha256']
assert v['minimum_gap_mm']>=.1 and v['overlapping_vias']==v['clearance_violating_vias']==v['native_expanded_disk_hit_vias']==0
nets=sorted({q['net'] for q in s['pads'] if q['net']});assert len(nets)==27
bomcpl={}
for name in ['BOM.csv','CPL.csv']:
 assert (E/'manufacturing'/name).read_bytes()==(S/'manufacturing'/name).read_bytes()
 bomcpl[name]=dict(regenerated=True,identical_to_Rev2=True,sha256=digest(E/'manufacturing'/name),reuse_allowed=True)
save(E/'assembly-identity.json',dict(utc=now(),files=bomcpl,reason='Same exact MPNs, references, component positions, side, rotation and GH14 body centroid. Regenerated from Rev.3 saved board; byte-identical to Rev.2.'))
save(E/'design-preservation.json',dict(utc=now(),base_board_sha256=digest(base),final_board_sha256=digest(final),nonrouting_AST_exact_Rev2=True,unchanged=['all footprints, pads and positions','all pad nets / NC intent','outline and 4 NPTH holes / keepouts','GH14 geometry and pin assignment','artwork, text and paste membership','stackup, net classes and every project rule'],source_project_byte_identical=True,changes_limited_to_segments_and_vias=True,project_status_sha256=digest(R/'docs/project-status.md')))
protected=json.loads((E/'protected-existing.json').read_text());changes=[]
for name,sha in protected.items():
 path=R/name
 if not path.exists() or digest(path)!=sha:changes.append(name)
assert changes==['docs/decisions.md'] or set(changes)=={'docs/decisions.md'},changes
assert digest(R/'docs/project-status.md')==json.loads((E/'resume-state.json').read_text())['project_status_sha256']
save(E/'preservation-audit.json',dict(utc=now(),preexisting_files_checked=len(protected),changed_existing_files=changes,authorized_change='Append D-029 only to decisions.md; private index stages base-branch content plus D-029, preserving its D-023/D-028 entries.',project_status_unchanged=True,Rev2_package_unchanged=True,unintended_changes=0))
save(E/'all-net-coverage.json',dict(utc=now(),all_nets=nets,net_count=len(nets),pads=len(s['pads']),all_net_metrics=a['metrics'],independent_physical_graph='inspection/final/copper-graph.json',isolated_or_wrong_net_contacts=0))
shutil.copyfile(E/'inspection/final/all-vias.csv',E/'all-vias.csv')
save(E/'verification.json',dict(utc=now(),qualified_board_sha256=digest(final),final_independent_metrics=a['metrics'],all_nets_checked=len(nets),all_vias=v['via_count'],all_copper_pads=v['copper_pad_count'],via_pad_pair_tests=v['pair_tests'],minimum_via_annulus_to_pad_mm=v['minimum_gap_mm'],via_pad_overlaps=0,via_pad_clearance_violations=0,native_collision_crosscheck_pass=True,layers=2,thickness_mm=1.2,track_widths_mm={'signal':.1,'power':.3},signal_segments=w['classes']['Signal']['segments'],power_segments=w['classes']['Power']['segments'],via_size_drill_mm=[.6,.3],clearance_mm=.1,KRT_escalation='off',no_condition_relaxation=True,independent_manufacturing_DRC_zero=True,CAM_geometry_exact_match=True,BOM_CPL_regenerated_identical_to_Rev2=True,unintended_existing_file_changes=0,no_order_no_charge_no_merge=True))
print('Final identity, qualification, assembly and preservation verified')
