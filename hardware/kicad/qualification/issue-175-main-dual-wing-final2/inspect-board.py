"""Independent DRC and canonical AST/copper coverage with frozen input project."""
from common import *
import collections,sexpdata as sx
from shapely.geometry import LineString
from shapely.ops import unary_union
label=sys.argv[1];source=E/'inputs'/label;raw=E/'runs'/label;w=E/'inspection'/label
if not (w/'main.kicad_pcb').exists():assert run(label+'-refill',['/usr/bin/python3',E/'refill.py',label])==0
if not (w/'drc.json').exists():assert run(label+'-drc',[B/'kicad/usr/bin/kicad-cli','pcb','drc','--format','json','--severity-all','-o',w/'drc.json',w/'main.kicad_pcb'])==0
reader=R/'hardware/kicad/qualification/eda-004g/resume-02/read-pcb.py'
if not (w/'snapshot.json').exists():assert run(label+'-snapshot',['/usr/bin/python3',reader,w/'main.kicad_pcb',w/'snapshot.json'])==0
if not (w/'connectivity.json').exists():assert run(label+'-connectivity',['/usr/bin/python3',E/'connectivity.py',label])==0
def children(n,k):return [x for x in n if isinstance(x,list) and x and str(x[0])==k]
def val(n,k):return children(n,k)[0][1:]
def clean(n):
 if not isinstance(n,list):return n
 if n and str(n[0])=='fill':n=[x for x in n if str(x)!='yes']
 return [clean(x) for x in n if not (isinstance(x,list) and x and str(x[0]) in ['filled_polygon','fill_segments','filled_areas_thickness'])]
def inv(n):return collections.Counter(sx.dumps(x) for x in clean(n)[1:] if not (isinstance(x,list) and x and str(x[0]) in ['segment','via']))
a=sx.loads((w/'canonical-input.kicad_pcb').read_text());b=sx.loads((w/'main.kicad_pcb').read_text());removed=list((inv(a)-inv(b)).elements());added=list((inv(b)-inv(a)).elements());missing=[];coverage=[]
for track in children(a,'segment'):
 candidates=[x for x in children(b,'segment') if all(val(x,k)==val(track,k) for k in ['width','layer','net'])]
 line=LineString([val(track,'start'),val(track,'end')]);g=unary_union([LineString([val(x,'start'),val(x,'end')]) for x in candidates]);length=line.difference(g).length
 row=dict(source=sx.dumps(track),uncovered_length_mm=length);(missing if length>.000002 else coverage).append(row)
oldvias=collections.Counter(sx.dumps(x) for x in children(a,'via'));newvias=collections.Counter(sx.dumps(x) for x in children(b,'via'));lostvias=list((oldvias-newvias).elements())
def delta(a,b,path=''):
 if isinstance(a,dict) and isinstance(b,dict):
  out=[]
  for k in sorted(set(a)|set(b)):
   if k not in a or k not in b:out.append(dict(path=path+'/'+k,before=a.get(k),after=b.get(k)))
   else:out.extend(delta(a[k],b[k],path+'/'+k))
  return out
 return [] if a==b else [dict(path=path,before=a,after=b)]
project=delta(json.loads((source/'main.kicad_pro').read_text()),json.loads((raw/'out.kicad_pro').read_text())) if (raw/'out.kicad_pro').exists() else []
save(w/'transfer-diff.json',dict(nonroute_removed=removed,nonroute_added=added,retained_route_coverage=coverage,missing_retained_tracks=missing,missing_retained_vias=lostvias,output_project_changes=project,fill_normalization='Only cache nodes and fill yes flag excluded; no design zone settings excluded.',raw_output_sha256=digest(raw/'out.kicad_pcb'),refilled_sha256=digest(w/'main.kicad_pcb')))
drc=json.loads((w/'drc.json').read_text());physical=json.loads((w/'physical-readback.json').read_text());graph=json.loads((w/'connectivity.json').read_text());printing={'text_height','silk_overlap','silk_over_copper'};material=[x for x in drc['violations'] if x['type'] not in printing]
metrics=dict(required_unconnected=None,wrong_net_contacts=None,material_violations=None,unexplained_transfer_changes=None)
unexplained=len(removed)+len(added)+len(missing)+len(lostvias)
if not drc['unconnected_items']:metrics=dict(required_unconnected=graph['required_unconnected'],wrong_net_contacts=graph['wrong_net_contacts'],material_violations=len(material),unexplained_transfer_changes=unexplained)
widthpass=all(float(x)>=.1 for x in physical['track_width_mm_counts']);viapass=all(x=='0.6/0.3' for x in physical['via_diameter_drill_mm_counts']);planepass=physical['tracks_per_layer'].get('In1.Cu',0)==0 and len(physical['zones'])==1 and physical['zones'][0]['filled'] and physical['zones'][0]['net']=='GND'
assessment=dict(utc=now(),label=label,metrics=metrics,measured_unconnected=len(drc['unconnected_items']),drc_type_counts=dict(collections.Counter(x['type'] for x in drc['violations'])),raw_material_count=len(material),raw_unexplained_count=unexplained,width_pass=widthpass,via_pass=viapass,plane_pass=planepass,all_44_nets_checked=graph['nets_checked']==44,pass_acceptance=not drc['unconnected_items'] and all(x==0 for x in metrics.values()) and widthpass and viapass and planepass and graph['nets_checked']==44,physical=physical)
save(w/'assessment.json',assessment);print(json.dumps(assessment,indent=2))
