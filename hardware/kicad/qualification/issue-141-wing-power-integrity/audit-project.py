"""Classify KRT measurement records; retain first strict assessment unchanged."""
from common import *
import sys,copy
cell=sys.argv[1];w=E/'inspection'/cell;raw=E/'runs'/cell;source=E/'cell-inputs'/cell
before=json.loads((source/'main.kicad_pro').read_text());after=json.loads((raw/'out.kicad_pro').read_text());W=json.loads((source/'condition.json').read_text())['width_mm']
records=after.pop('kicad_routing_tools');assert after==before
assert set(records)=={'fab_floor_origin','records_rev','power_widths'}
assert records['power_widths']=={'HALL_5V':W,'GND':W}
assert records['fab_floor_origin']==dict(min_hole_clearance=.2,min_through_hole_diameter=.3,min_track_width=.1,min_via_annular_width=.1,min_via_diameter=.6,min_via_drill=.3)
assert records['records_rev']==2
assessment=json.loads((w/'assessment.json').read_text());width=json.loads((w/'width-audit.json').read_text())
save(w/'first-strict-assessment.json',assessment);save(w/'first-strict-width-audit.json',width)
assert width['tracks_below_pinned']==0 and width['incorrect_vias']==0 and all(q['below_required']==0 for q in width['classes'].values())
width['unexplained_project_changes']=[];width['project_settings_byte_semantically_unchanged']=True
width['allowed_additional_measurement_records']=records
save(w/'width-audit.json',width)
assessment.update(width_pass=True,pass_acceptance=assessment['measured_unconnected']==0 and all(v==0 for v in assessment['metrics'].values()) and assessment['nonroute_snapshot_unchanged'],project_audit_correction='Initial comparator only allowed fab_floor_origin; power_widths are measured records exactly equal to pinned values. Every other project key equals input.',supplemental_audit_utc=now())
save(w/'project-record-audit.json',dict(all_project_settings_identical=True,metadata_only_addition=records,no_reroute=True,no_graph_or_drc_metric_changed=True,utc=now()))
save(w/'assessment.json',assessment);save(raw/'report.json',assessment)
print(json.dumps(assessment,indent=2))
