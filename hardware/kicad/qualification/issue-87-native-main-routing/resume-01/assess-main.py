"""Terminal measurements saved before verdict; router messages are not acceptance."""
import json,sys,importlib.util,collections
from pathlib import Path
import sexpdata as sx
from shapely.geometry import LineString
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('checker',ROOT.parent/'check-main.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
before_file,after_file,before_snapshot,after_snapshot,drc_file,out=sys.argv[1:]
a=json.loads(Path(before_snapshot).read_text());b=json.loads(Path(after_snapshot).read_text());d=json.loads(Path(drc_file).read_text())
def nonroute(p):
    tree=sx.loads(Path(p).read_text());return collections.Counter(sx.dumps(n) for n in tree[1:] if not isinstance(n,list) or not n or str(n[0]) not in ['segment','via'])
nonroute_same=nonroute(before_file)==nonroute(after_file)
snapshot_same=all(a[k]==b[k] for k in a if k!='tracks')
local=[]
for t in a['tracks']:
    source=LineString([t['start'],t['end']]);candidates=[x for x in b['tracks'] if x['kind']=='track' and all(x[k]==t[k] for k in ['width','net','layer'])]
    copper=unary_union([LineString([x['start'],x['end']]) for x in candidates]);missing=source.difference(copper).length
    local.append(dict(source=t,missing_centerline_length_mm=missing,preserved=missing<=m.C['tolerance_mm']))
track_rules=all((t['width']==.2 and t['layer'] in [0,2]) if t['kind']=='track' else (t['kind']=='via' and t['size']==.6 and t['drill']==.3 and t['layers']==[0,2]) for t in b['tracks'])
graph=m.snapshot_graph(b)
# Count physical required lands, including repeated pad numbers independently.
net_of={p['ref']+'.'+p['number']:p['net'] for p in a['pads'] if p['attribute']!='NPTH'}
by_net={}
for root,ids in graph['groups'].items():
    counts=collections.Counter(net_of[id] for id in ids if id in net_of and net_of[id])
    for net,count in counts.items():by_net.setdefault(net,[]).append(count)
endpoint_deficits={n:sum(counts)-max(counts) for n,counts in by_net.items() if len(counts)>1}
printing={'text_height','silk_overlap','silk_over_copper'}
material=[v for v in d['violations'] if v['type'] not in printing]
print_warnings=[v for v in d['violations'] if v['type'] in printing]
passed=nonroute_same and snapshot_same and all(x['preserved'] for x in local) and track_rules and not graph['shorts'] and not graph['disconnected'] and not material and not d['unconnected_items']
r=dict(status='INITIAL_PASS_PENDING_CONFIRMATION' if passed else 'ROUTING_BLOCKED / INITIAL_FAIL',all_conditions_pass=passed,nonroute_semantics_identical=nonroute_same,snapshot_nonroute_equal=snapshot_same,source_local_copper=local,track_width_via_layer_rules_preserved=track_rules,required_physical_endpoint_deficits_outside_largest_net_island=sum(endpoint_deficits.values()),endpoint_deficit_definition='For every required net, physical required lands outside its largest connected island, counting duplicate-number lands individually; not KiCad airwire count.',per_net_endpoint_deficits=endpoint_deficits,independent_disconnected_net_count=len(graph['disconnected']),independent_disconnected_component_counts=graph['disconnected'],wrong_net_actual_contact_pairs=len(graph['shorts']),wrong_net_contacts=graph['shorts'],kicad_unconnected_items=len(d['unconnected_items']),targeted_material_violations=len(material),targeted_material_details=material,unexplained_transfer_changes=0 if nonroute_same and snapshot_same and all(x['preserved'] for x in local) else None,printing_warning_count=len(print_warnings),printing_warning_types=dict(collections.Counter(x['type'] for x in print_warnings)),other_snapshot=dict(pads=len(b['pads']),tracks=len(b['tracks']),vias=sum(t['kind']=='via' for t in b['tracks'])),no_confirmation_unless_all_conditions_pass=True)
Path(out).write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:r[k] for k in ['status','required_physical_endpoint_deficits_outside_largest_net_island','independent_disconnected_net_count','wrong_net_actual_contact_pairs','kicad_unconnected_items','targeted_material_violations','unexplained_transfer_changes','printing_warning_count']}))
