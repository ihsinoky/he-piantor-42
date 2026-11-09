"""Scope/PCB/XML audit independent of authoring; no routing or rule changes."""
from common import *
import sexpdata as sx,collections,xml.etree.ElementTree as ET
V=E.parent/'issue-196-main-rev4-phaseb';w=E/'inspection/final'
def tag(x):return str(x[0]) if isinstance(x,list) and x else ''
def clean(x):
 if not isinstance(x,list):return x
 if tag(x)=='fill':x=[q for q in x if str(q)!='yes']
 return [clean(q) for q in x if tag(q) not in ['filled_polygon','fill_segments','filled_areas_thickness']]
a=sx.loads((V/'inspection/final/main.kicad_pcb').read_text());b=sx.loads((w/'main.kicad_pcb').read_text())
def fpref(n):return next(x[2] for x in n if tag(x)=='property' and x[1]=='Reference')
fa={fpref(n):n for n in a if tag(n)=='footprint'};fb={fpref(n):n for n in b if tag(n)=='footprint'}
assert fa.keys()==fb.keys()
changed=[r for r in fa if fa[r]!=fb[r]];assert changed==['J4'],changed
nonroute=lambda q:collections.Counter(sx.dumps(clean(n)) for n in q[1:] if tag(n) not in ['segment','via','footprint'])
assert nonroute(a)==nonroute(b),'Nonroute design data changed'
def ident(n):return next(x[1] for x in n if tag(x)=='uuid')
ta={ident(n):n for n in a if tag(n) in ['segment','via']};tb={ident(n):n for n in b if tag(n) in ['segment','via']}
removed=[n for k,n in ta.items() if k not in tb];added=[n for k,n in tb.items() if k not in ta];mutated=[k for k in ta.keys() & tb.keys() if ta[k]!=tb[k]];assert not mutated
netnames={n[1]:n[2] for n in a if tag(n)=='net'}
nets=set();points=[];changes=[]
for action,items in [('removed',removed),('added',added)]:
 for n in items:
  assert tag(n)=='segment','No via changes allowed'
  fields={tag(x):x[1:] for x in n[1:] if isinstance(x,list)};net=netnames[fields['net'][0]];nets.add(net)
  points.extend([fields['start'],fields['end']]);assert fields['layer']==['F.Cu']
  changes.append(dict(action=action,uuid=ident(n),net=net,start=fields['start'],end=fields['end'],width=fields['width'][0]))
assert nets=={'GND','VBUS','USB_DM_ESD','USB_DP_ESD'},nets
assert all(97.5<=x<=102.5 and 91<=y<=96 for x,y in points)
s=json.loads((w/'snapshot.json').read_text());old=json.loads((V/'inspection/final/snapshot.json').read_text())
for c in s['components']:
 prev=next(q for q in old['components'] if q['ref']==c['ref']);assert prev['position']==c['position'] and prev['angle']==c['angle']
def xmlpins(path):
 root=ET.parse(path);return {(n.get('ref'),n.get('pin')):net.get('name').removeprefix('/') for net in root.findall('.//nets/net') for n in net.findall('node') if not n.get('ref').startswith('#FLG') and not net.get('name').startswith('unconnected-')}
xold=xmlpins(V/'schematic/main.net.xml');xnew=xmlpins(E/'schematic/main.net.xml');assert xold==xnew
pcb={(a['ref'],a['number']):a['net'] for a in s['pads'] if a['number']};assert {k:v for k,v in pcb.items() if v}==xnew
assert (w/'main.kicad_pro').read_bytes()==(V/'inspection/final/main.kicad_pro').read_bytes()
report=dict(pass_check=True,rev4_sha256=digest(V/'inspection/final/main.kicad_pcb'),rev5_sha256=digest(w/'main.kicad_pcb'),changed_footprints=changed,changed_copper_nets=sorted(nets),changed_logical_pins=0,logical_netted_pins=len(xnew),all_62_positions_and_angles_preserved=True,unchanged_tracks_and_vias=len(ta)-len(removed),removed_tracks=len(removed),added_tracks=len(added),changed_vias=0,route_endpoint_bounds_mm=[min(x for x,y in points),min(y for x,y in points),max(x for x,y in points),max(y for x,y in points)],outline_holes_zones_rules_and_other_root_nodes_unchanged=True,project_byte_identical=True,changes=changes)
save(E/'rev4-diff.json',report);print(json.dumps(report,ensure_ascii=False,indent=2))
