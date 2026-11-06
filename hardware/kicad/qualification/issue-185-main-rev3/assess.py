"""Verify four independent metrics; every allowed route delta has explicit UUID evidence."""
from common import *
import sexpdata as sx,collections
label='final';w=E/'inspection'/label;old=E.parent/'issue-175-main-dual-wing-final2';a=sx.loads((w/'canonical-baseline.kicad_pcb').read_text());b=sx.loads((w/'main.kicad_pcb').read_text())
def children(n,k):return [x for x in n if isinstance(x,list) and x and str(x[0])==k]
def val(n,k):return children(n,k)[0][1:]
def clean(n):
 if not isinstance(n,list):return n
 if n and str(n[0])=='fill':n=[x for x in n if str(x)!='yes']
 return [clean(x) for x in n if not (isinstance(x,list) and x and str(x[0]) in ['filled_polygon','fill_segments','filled_areas_thickness'])]
def inv(n):return collections.Counter(sx.dumps(x) for x in clean(n)[1:] if not (isinstance(x,list) and x and str(x[0]) in ['segment','via']))
removed=list((inv(a)-inv(b)).elements());added=list((inv(b)-inv(a)).elements())
byid=lambda n,k:{str(val(x,'uuid')[0]):x for x in children(n,k)}
sa,sb=byid(a,'segment'),byid(b,'segment');va,vb=byid(a,'via'),byid(b,'via')
changes=json.loads((E/'straight33/changes.json').read_text())+json.loads((E/'local35/changes.json').read_text());moves={r['via_uuid']:r for r in changes};failures=[]
for uid,v in va.items():
 if uid not in vb:failures.append(dict(uuid=uid,reason='missing via'));continue
 n=vb[uid]
 if uid in moves:
  expected=moves[uid]['position_mm'];actual=val(n,'at')
  if max(abs(x-y) for x,y in zip(expected,actual))>1e-9:failures.append(dict(uuid=uid,reason='wrong movement'))
  x=[t for t in v if not (isinstance(t,list) and t and str(t[0])=='at')];y=[t for t in n if not (isinstance(t,list) and t and str(t[0])=='at')]
  if x!=y:failures.append(dict(uuid=uid,reason='other via property changed'))
 elif v!=n:failures.append(dict(uuid=uid,reason='unplanned via change'))
if set(va)!=set(vb):failures.append(dict(reason='via set changed'))
for uid,t in sa.items():
 if sb.get(uid)!=t:failures.append(dict(uuid=uid,reason='retained segment changed'))
ids={s['uuid'] for r in changes if 'stubs' in r for s in r['stubs']}|{uid for r in changes if 'paths' in r for path in r['paths'] for uid in path['track_uuids']}
if set(sb)-set(sa)!=ids:failures.append(dict(reason='new segment set mismatch'))
# Check actual new segments against recorded endpoint/width/net/layer, independently of UUID set.
netcodes={str(x[2]):int(x[1]) for x in children(b,'net')}
for r in changes:
 planned=[]
 for s in r.get('stubs',[]):
  an=s['anchor'];planned.append((s['uuid'],an['position_mm'],r['position_mm'],an['layer'],an['width_mm']))
 for path in r.get('paths',[]):
  planned.extend((uid,aa,bb,path['layer'],path['width_mm']) for uid,aa,bb in zip(path['track_uuids'],path['points_mm'],path['points_mm'][1:]) if aa!=bb)
 for uid,aa,bb,layer,width in planned:
  t=sb[uid]
  if any(max(abs(x-y) for x,y in zip(val(t,key),expected))>1e-9 for key,expected in [('start',aa),('end',bb)]) or str(val(t,'layer')[0])!=layer or val(t,'width')!=[width] or val(t,'net')!=[netcodes[r['net']]]:failures.append(dict(uuid=uid,reason='new segment geometry mismatch'))
transfer=dict(nonroute_removed=removed,nonroute_added=added,route_delta_failures=failures,baseline_vias=len(va),final_vias=len(vb),explained_via_moves=len(moves),retained_segments=len(sa),new_segments=len(ids),input_sha256=digest(old/'inspection/final/main.kicad_pcb'),output_sha256=digest(w/'main.kicad_pcb'))
save(w/'transfer-diff.json',transfer)
drc=json.loads((w/'drc.json').read_text());graph=json.loads((w/'connectivity.json').read_text());printing={'text_height','silk_overlap','silk_over_copper'};material=[x for x in drc['violations'] if x['type'] not in printing]
metrics=dict(required_unconnected=graph['required_unconnected'],wrong_net_contacts=graph['wrong_net_contacts'],material_violations=len(material),unexplained_transfer_changes=len(removed)+len(added)+len(failures))
snap=json.loads((w/'snapshot.json').read_text());tracks=snap['tracks'];width=all(t['width']>=.1 for t in tracks if t['kind']=='track');via=all(t['size']==.6 and t['drill']==.3 for t in tracks if t['kind']=='via');plane=graph['filled_zones'] and all(z['net']=='GND' and z['layer']=='In1.Cu' for z in graph['filled_zones']) and not any(t['kind']=='track' and t['layer']==4 for t in tracks)
out=dict(metrics=metrics,raw_material_count=len(material),raw_unexplained_count=metrics['unexplained_transfer_changes'],measured_unconnected=len(drc['unconnected_items']),drc_type_counts=dict(collections.Counter(x['type'] for x in drc['violations'])),all_44_nets_checked=graph['nets_checked']==44,width_pass=width,via_pass=via,plane_pass=bool(plane),pass_acceptance=all(x==0 for x in metrics.values()) and not drc['unconnected_items'] and graph['nets_checked']==44 and width and via and bool(plane))
save(w/'assessment.json',out);print(json.dumps(out,indent=2));assert out['pass_acceptance']
