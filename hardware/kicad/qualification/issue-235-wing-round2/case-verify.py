"""Reload delivered proposal geometry; compare full connected cable, not bare bundle."""
from pathlib import Path
import json,math
from build123d import import_step,Compound
E=Path(__file__).resolve().parent;ROOT=E.parents[3];rows=[]
def vol(a,b):
 hit=a.intersect(b);return sum(s.volume for s in hit) if hit else 0.
for r in json.loads((E/'case/summary.json').read_text()):
 pitch,side=r['variant'].split('-');out=E/'case'/pitch
 original=import_step(ROOT/f'hardware/case/issue-228-final/{pitch}/tray-{side}.step');bundle=import_step(out/f'trial-GH-{side}.step');fanout=import_step(out/f'actual-GH-exit-{side}.step');proposal=import_step(out/f'tray-{side}-channel-candidate.step');route=Compound(children=[bundle,fanout])
 assert all(a.is_valid for a in (original,bundle,fanout,proposal));assert len(proposal.solids())==1
 before=vol(route,original);after=vol(route,proposal);removed=original.volume-proposal.volume
 expected=next(a['overlap_mm3'] for a in r['trial_collisions'] if a['obstacle']=='tray-'+side)
 assert math.isclose(before,expected,abs_tol=.002,rel_tol=1e-5),(r['variant'],before,expected)
 assert after<1e-5
 assert math.isclose(removed,r['wall_channel_removed_mm3'],abs_tol=.002,rel_tol=1e-5)
 assert abs(bundle.bounding_box().min.Z-2.5)<1e-5
 assert r['trial_is_connected_to_GH'] and r['gh_reserved_floor_gap_mm']>=.5
 rows.append({'variant':r['variant'],'STEP_valid':True,'original_wall_overlap_mm3':before,'with_proposal_overlap_mm3':after,'removed_mm3':removed,'original_case_pass':False,'proposal_route_geometry_clear':not r['post_overlaps'] and all(a['obstacle']=='tray-'+side for a in r['trial_collisions']),'tolerance_certified_harness':False})
 print(r['variant'],'STEP replay pass',flush=True)
(E/'case/verification.json').write_text(json.dumps({'saved_STEP_checks_pass':True,'rows':rows,'production_case_unchanged':True},indent=2)+'\n')
