"""Independent KiCad DRC after refill and semantic transfer comparison."""
from helpers import *
import collections
sys.path.insert(0,str(RT/'geometry/lib/python3.12/site-packages'))
import sexpdata as sx
stage,router=sys.argv[1:3];attempt=sys.argv[3] if len(sys.argv)>3 else '01'
label=stage if attempt=='01' else stage+'-'+attempt
source=(E if stage=='main' else A)/'inputs'/label;raw=A/'runs'/label/router;w=A/'inspection'/label/router
if not (E/'processes'/('amend01-'+label+'-'+router+'-refill')/'record.json').exists():
 assert run('amend01-'+label+'-'+router+'-refill',['/usr/bin/python3',A/'read-refill.py',stage,router,attempt])==0
if not (E/'processes'/('amend01-'+label+'-'+router+'-snapshot')/'record.json').exists():
 assert run('amend01-'+label+'-'+router+'-snapshot',['/usr/bin/python3',R/'hardware/kicad/qualification/eda-004g/resume-02/read-pcb.py',w/'main.kicad_pcb',w/'snapshot.json'])==0
if not (E/'processes'/('amend01-'+label+'-'+router+'-drc')/'record.json').exists():
 assert run('amend01-'+label+'-'+router+'-drc',[RT/'kicad/usr/bin/kicad-cli','pcb','drc','--format','json','--severity-all','-o',w/'drc.json',w/'main.kicad_pcb'])==0
def children(t,tag):return [x for x in t if isinstance(x,list) and x and str(x[0])==tag]
def inventory(t,exclude=()):return collections.Counter(sx.dumps(n) for n in t[1:] if not isinstance(n,list) or not n or str(n[0]) not in exclude)
def trimfill(n):
 if not isinstance(n,list):return n
 return [trimfill(x) for x in n if not (isinstance(x,list) and x and str(x[0]) in ['filled_polygon','fill_segments','filled_areas_thickness'])]
before=sx.loads((w/'canonical-input.kicad_pcb').read_text());after=sx.loads((w/'main.kicad_pcb').read_text())
a=inventory(trimfill(before),('segment','via'));b=inventory(trimfill(after),('segment','via'))
removed=list((a-b).elements());added=list((b-a).elements())
# Keep original tracks on their original layers; UUID preservation is checked too.
old=collections.Counter(sx.dumps(n) for n in children(before,'segment')+children(before,'via'))
new=collections.Counter(sx.dumps(n) for n in children(after,'segment')+children(after,'via'))
uuid_changes=list((old-new).elements())
# Same physical copper can be split by a router junction or re-UUIDed by SES.
# Use the established #87 centerline coverage rule, preserving layer/net/width.
from shapely.geometry import LineString
from shapely.ops import unary_union
def val(n,tag):return children(n,tag)[0][1:]
missing=[];explained_routes=[]
for track in children(before,'segment'):
 candidates=[n for n in children(after,'segment') if all(val(n,k)==val(track,k) for k in ['width','layer','net'])]
 original=LineString([val(track,'start'),val(track,'end')])
 coverage=unary_union([LineString([val(n,'start'),val(n,'end')]) for n in candidates])
 uncovered=original.difference(coverage).length
 row=dict(source=sx.dumps(track),uncovered_length_mm=uncovered)
 (missing if uncovered>0.000002 else explained_routes).append(row)

project=delta(json.loads((source/'main.kicad_pro').read_text()),json.loads((raw/'out.kicad_pro').read_text())) if (raw/'out.kicad_pro').exists() else []
save(w/'transfer-diff.json',dict(nonroute_removed=removed,nonroute_added=added,original_routes_missing=missing,source_track_coverage=explained_routes,UUID_sensitive_route_differences=uuid_changes,output_project_changes=project,explained='Both inputs canonicalized with the same KiCad saver; only zone fill-cache nodes excluded after required refill. Original segment centerline coverage checked at 2nm; SES UUID reassignment and collinear splits explained separately.',raw_output_sha256=sha(raw/'out.kicad_pcb'),refilled_output_sha256=sha(w/'main.kicad_pcb')))
drc=json.loads((w/'drc.json').read_text());physical=json.loads((w/'physical-readback.json').read_text())
printing={'text_height','silk_overlap','silk_over_copper'}
material=[v for v in drc['violations'] if v['type'] not in printing]
shorts=[v for v in drc['violations'] if v['type'] in ['shorting_items','short_circuit']]
unconnected=drc['unconnected_items'];metrics=dict(required_unconnected=None,wrong_net_contacts=None,material_violations=None,unexplained_transfer_changes=None)
if not unconnected:metrics=dict(required_unconnected=0,wrong_net_contacts=len(shorts),material_violations=len(material),unexplained_transfer_changes=len(removed)+len(added)+len(missing))
width_pass=all(float(k)>=.2 for k in physical['track_width_mm_counts'])
via_pass=all(k=='0.6/0.3' for k in physical['via_diameter_drill_mm_counts'])
plane_pass=physical['In1_signal_tracks']==0 and len(physical['zones'])==1 and physical['zones'][0]['filled'] and physical['zones'][0]['net']==('GND' if stage=='main' else 'N')
accept=not unconnected and all(v==0 for v in metrics.values()) and width_pass and via_pass and plane_pass
save(w/'independent.json',dict(utc=utc(),stage=stage,router=router,pass_acceptance=accept,metrics=metrics,measured_unconnected_count=len(unconnected),unconnected_net_endpoint_list=unconnected,raw_material_DRC_count=len(material),raw_short_DRC_count=len(shorts),drc_type_counts=dict(collections.Counter(v['type'] for v in drc['violations'])),width_pass=width_pass,via_pass=via_pass,plane_role_pass=plane_pass,original_project_used_for_DRC=True,zone_refill_before_DRC=True,output_project_changes=project,unexplained_change_raw_count=len(removed)+len(added)+len(missing),physical=physical))
print(json.dumps(dict(stage=stage,router=router,pass_acceptance=accept,unconnected=len(unconnected),metrics=metrics,nonroute_removed=len(removed),nonroute_added=len(added),missing_original_routes=len(missing),drc_types=collections.Counter(v['type'] for v in drc['violations'])),indent=2))
