"""Reload the delivered STEP files; independently reproduce key collision volumes."""
from pathlib import Path
import json,math
from build123d import import_step
E=Path(__file__).resolve().parent;ROOT=E.parents[3];CASE=ROOT/'hardware/case/issue-228-final'
def volume(a,b):
 result=a.intersect(b);return sum(s.volume for s in result) if result else 0.
rows=[]
for row in json.loads((E/'case/summary.json').read_text()):
 pitch,side=row['variant'].split('-');out=E/'case'/pitch
 source=import_step(CASE/pitch/f'tray-{side}.step');trial=import_step(out/f'trial-GH-{side}.step');exitshape=import_step(out/f'actual-GH-exit-{side}.step');candidate=import_step(out/f'tray-{side}-channel-candidate.step')
 assert all(s.is_valid for s in (source,trial,exitshape,candidate));assert len(candidate.solids())==1
 overlap=volume(trial,source);exitoverlap=volume(exitshape,source);after=volume(trial,candidate)
 assert math.isclose(overlap,row['trial_collisions'][0]['overlap_mm3'],rel_tol=1e-5,abs_tol=1e-4)
 assert math.isclose(exitoverlap,row['exit_floor_collisions'][0]['overlap_mm3'],rel_tol=1e-5,abs_tol=1e-4)
 assert exitoverlap>0 and overlap>0 and after<1e-5
 assert math.isclose(source.volume-candidate.volume,row['wall_channel_removed_mm3'],rel_tol=1e-5,abs_tol=1e-4)
 bb=exitshape.bounding_box();assert abs(bb.min.Z+4.8)<1e-5
 rows.append({'variant':row['variant'],'source_wall_overlap_mm3':overlap,'actual_GH_exit_floor_overlap_mm3':exitoverlap,'channel_candidate_overlap_mm3':after,'exit_min_z_mm':bb.min.Z,'valid_STEP_solids':True,'design_pass':False})
(E/'case/verification.json').write_text(json.dumps({'saved_STEP_reload_checks_pass':True,'design_pass':False,'rows':rows},indent=2)+'\n');print('STEP reload checks pass; all actual GH exits still collide')
