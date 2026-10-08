"""Synthetic source-intent reconciliation, independent of converter/router."""
import json, math, sys
from pathlib import Path
from process import save,EVIDENCE,utc,digest
TOL=1e-6  # millimetres, measurement rounding only
EXPECTED=[
 dict(ref='U_TX',pin='1',net='SIG',x=-4,y=2,shape='rect',size=[1,1],drill=[0,0],plated=False,layers=['top']),
 dict(ref='U_TX',pin='2',net='GND',x=-5,y=0,shape='oval',size=[1,2.1],drill=[.6,1.7],plated=True,layers=['top','bottom']),
 dict(ref='U_TX',pin='2',net='GND',x=-3,y=0,shape='oval',size=[1,1.6],drill=[.6,1.2],plated=True,layers=['top','bottom']),
 dict(ref='U_RX',pin='1',net='SIG',x=2,y=0,shape='rect',size=[1,1],drill=[0,0],plated=False,layers=['top']),
 dict(ref='U_RX',pin='2',net='GND',x=4,y=0,shape='rect',size=[1,1],drill=[0,0],plated=False,layers=['top'])]
RULES={'min_trace_width':.2,'min_via_hole_diameter':.3,'min_via_pad_diameter':.6,
 'min_trace_to_pad_edge_clearance':.2,'min_pad_edge_to_pad_edge_clearance':.2,
 'min_trace_to_hole_edge_clearance':.2,'min_via_hole_edge_to_via_hole_edge_clearance':.2,
 'min_plated_hole_drill_edge_to_drill_edge_clearance':.2,'min_board_edge_clearance':.2}


def close(a,b):
 return math.isclose(a,b,rel_tol=0,abs_tol=TOL)


def check(data):
 def rows(kind):return [x for x in data if x['type']==kind]
 def index(kind,key):return {x[key]:x for x in rows(kind)}
 assert not [x for x in data if x['type'].endswith('_error')], 'source circuit errors'
 comps=index('source_component','source_component_id');ports=index('source_port','source_port_id')
 assert sorted(x['name'] for x in comps.values())==['U_RX','U_TX']
 # Derive net memberships from logical edges and internal connections, not labels.
 parent={k:k for k in ports}
 def find(k):
  while parent[k]!=k:k=parent[k]
  return k
 def union(a,b):parent[find(b)]=find(a)
 for x in rows('source_component_internal_connection'):
  ids=x['connected_source_port_ids']
  for p in ids[1:]:union(ids[0],p)
 assignments={}
 nets=index('source_net','source_net_id')
 for x in rows('source_trace'):
  ids=x['connected_source_port_ids']
  for p in ids[1:]:union(ids[0],p)
 for x in rows('source_trace'):
  names=[nets[n]['name'] for n in x['connected_source_net_ids']]
  for p in x['connected_source_port_ids']:
   assignments.setdefault(find(p),set()).update(names)
 assert all(len(v)==1 for v in assignments.values()), 'source net short'
 def net(p):return next(iter(assignments[find(p)]))
 pp=index('pcb_port','pcb_port_id')
 physical=[]
 for kind in ['pcb_smtpad','pcb_plated_hole']:
  for x in rows(kind):
   port=ports[pp[x['pcb_port_id']]['source_port_id']]
   pin=str(port.get('pin_number',2 if 'pin2' in port['port_hints'] else 'unknown'))
   physical.append(dict(id=x.get('pcb_smtpad_id',x.get('pcb_plated_hole_id')),ref=comps[port['source_component_id']]['name'],pin=pin,net=net(port['source_port_id']),x=x['x'],y=x['y'],shape=x['shape'],size=[x['width'],x['height']] if kind=='pcb_smtpad' else [x['outer_width'],x['outer_height']],drill=[0,0] if kind=='pcb_smtpad' else [x['hole_width'],x['hole_height']],plated=kind=='pcb_plated_hole',layers=[x['layer']] if kind=='pcb_smtpad' else x['layers']))
 assert len(physical)==len(EXPECTED), 'missing/additional physical pad'
 for e in EXPECTED:
  matches=[a for a in physical if a['ref']==e['ref'] and a['pin']==e['pin'] and close(a['x'],e['x']) and close(a['y'],e['y'])]
  assert len(matches)==1, 'physical pad identity/position'
  a=matches[0]
  for k in ['net','shape','plated','layers']:assert a[k]==e[k], 'pad '+k
  for k in ['size','drill']:assert all(close(v,w) for v,w in zip(a[k],e[k])), 'pad '+k
 board=rows('pcb_board');assert len(board)==1
 b=board[0]
 for k,v in {'width':20,'height':16,'thickness':1.2,'num_layers':2,**RULES}.items():assert close(b[k],v), 'board/rule '+k
 assert b['center']=={'x':0,'y':0}
 pc=rows('pcb_component')
 for c in pc:
  ref=comps[c['source_component_id']]['name']
  assert close(c['rotation'],90 if ref=='U_RX' else 0), 'component rotation'
  assert close(c['display_offset_x'],4 if ref=='U_RX' else -4) and close(c['display_offset_y'],0), 'component anchor'
 holes=rows('pcb_hole');assert len(holes)==1
 h=holes[0];assert h['hole_shape']=='circle' and close(h['x'],-4) and close(h['y'],-3) and close(h['hole_diameter'],.65), 'NPTH geometry'
 assert not rows('pcb_via') and not rows('pcb_copper_pour'), 'stock routing copper'
 traces=rows('pcb_trace');assert len(traces)==1, 'only one allowed local bond'
 tr=traces[0];src=index('source_trace','source_trace_id')[tr['source_trace_id']]
 assert src['name']=='LOCAL_BOND' and nets[src['connected_source_net_ids'][0]]['name']=='GND', 'local net/provenance'
 route=tr['route'];assert len(route)==2, 'local segment inventory'
 for p,(x,y) in zip(route,[(-5,0),(-3,0)]):
  assert p['route_type']=='wire' and p['layer']=='top' and close(p['width'],.2) and close(p['x'],x) and close(p['y'],y), 'local copper shape/position/layer'
 # Circuit checks for this defined synthetic output->input graph.
 semantics={}
 for p in ports.values():
  if 'pin_number' not in p:continue  # duplicate physical land inherits logical pin2
  key=comps[p['source_component_id']]['name']+'.'+str(p['pin_number'])
  attr='output' if p.get('is_output') else 'input' if p.get('is_input') else 'passive' if p.get('is_passive') else 'undefined'
  semantics[key]={'type':attr,'net':net(p['source_port_id'])}
 assert semantics=={'U_TX.1':{'type':'output','net':'SIG'},'U_TX.2':{'type':'passive','net':'GND'},'U_RX.1':{'type':'input','net':'SIG'},'U_RX.2':{'type':'passive','net':'GND'}}, 'pin semantics'
 return {'status':'PASS','physical_pads':physical,'components':pc,'board':b,'npth':h,'local_bond':tr,'source_semantics':semantics,'global_stock_tracks':0,'vias':0,'pours':0,'measurement_tolerance_mm':TOL,'warnings':[x for x in data if x['type'].endswith('_warning')],'circuit_check':'Defined SIG has exactly one output and one input; GND has passive endpoints; duplicate GND internal relation reconciled. Not real-device/Main ERC.'}

if __name__=='__main__':
 p=Path(sys.argv[1]);data=json.loads(p.read_text())
 try:
  result=check(data)
 except Exception as e:
  save(EVIDENCE/'input-reconciliation.json',{'status':'FAIL','error':repr(e),'raw_sha256':digest(p),'observed_utc':utc()});raise
 save(EVIDENCE/'input-reconciliation.json',result)
 print('source/Circuit JSON reconciliation PASS')
