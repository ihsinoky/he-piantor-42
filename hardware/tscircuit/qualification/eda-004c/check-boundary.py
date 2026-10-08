"""Reconcile saved KiCad inventory with source intent. No tool launch or repair."""
import importlib.util,json,math,re,sys
from pathlib import Path
from process import EVIDENCE,save,utc
spec=importlib.util.spec_from_file_location('inputcheck',Path(__file__).with_name('check-input.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def sexpr(text):
 tokens=re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+',text)
 stack=[];top=[]
 for t in tokens:
  if t=='(':
   x=[]
   if stack:stack[-1].append(x)
   else:top.append(x)
   stack.append(x)
  elif t==')':
   if not stack:raise ValueError('unbalanced close')
   stack.pop()
  else:
   if not stack:raise ValueError('token outside root')
   stack[-1].append(json.loads(t) if t.startswith('"') else t)
 if stack or len(top)!=1:raise ValueError('unbalanced/root count')
 return top[0]

def children(node,key):return [a for a in node if isinstance(a,list) and a and a[0]==key]
def one(node,key):
 items=children(node,key)
 if len(items)!=1:raise ValueError('expected exactly one '+key)
 return items[0]

def walk(node,key):
 if isinstance(node,list):
  if node and node[0]==key:yield node
  for c in node:
   if isinstance(c,list):yield from walk(c,key)

def schematic_inventory(text):
 root=sexpr(text);lib=one(root,'lib_symbols');defs=children(lib,'symbol')
 definitions=[]
 for d in defs:
  pins=[]
  for p in walk(d,'pin'):
   pins.append({'number':one(p,'number')[1],'name':one(p,'name')[1],'type':p[1]})
  definitions.append({'lib_id':d[1],'pins':pins})
 instances=[]
 for a in children(root,'symbol'):
  props={p[1]:p[2] for p in children(a,'property')}
  instances.append({'ref':props.get('Reference'),'lib_id':one(a,'lib_id')[1]})
 return {'definitions':definitions,'instances':instances}

def compare(inv,pro,sch):
 errors=[];maps=[];c=inv['constants']
 def issue(kind,**details):errors.append({'kind':kind,**details})
 def eq(a,b):return m.close(a,b)
 def pair(a,b):return len(a)==len(b) and all(eq(x,y) for x,y in zip(a,b))
 if inv['thickness_mm']!=1.2 or inv['copper_layers']!=2:issue('stack')
 if sorted(x['ref'] for x in inv['components'])!=['U_RX','U_TX']:issue('component_identity')
 raw=json.loads((EVIDENCE/'input-reconciliation.json').read_text())
 # Centroid/anchor distinction is explicit; PCB positions use raw centroid.
 for comp in raw['components']:
  ref='U_TX' if comp['source_component_id']=='source_component_0' else 'U_RX'
  target=[100+comp['center']['x'],100-comp['center']['y']]
  a=next((x for x in inv['components'] if x['ref']==ref),None)
  if not a or not pair(a['position'],target) or not eq(a['rotation'],comp['rotation']) or a['layer']!='F.Cu':issue('component_transform',ref=ref)
 electrical=[a for a in inv['pads'] if a['attribute']!=c['PAD_ATTRIB_NPTH']]
 if len(electrical)!=5:issue('physical_pad_inventory',actual=len(electrical))
 for e in m.EXPECTED:
  target=[100+e['x'],100-e['y']]
  found=[a for a in electrical if a['ref']==e['ref'] and a['number']==e['pin'] and pair(a['position'],target)]
  key={'ref':e['ref'],'pin':e['pin'],'source_xy':[e['x'],e['y']],'kicad_xy':target}
  if len(found)!=1:
   issue('physical_pad_identity_position',**key);continue
  a=found[0];maps.append({**key,'expected':e,'actual':a})
  if a['net']!=e['net']:issue('physical_pad_net',**key,expected=e['net'],actual=a['net'])
  if not pair(a['size'],e['size']):issue('pad_size',**key)
  if not pair(a['drill'],e['drill']):issue('pad_drill',**key)
  shape=c['PAD_SHAPE_OVAL'] if e['shape']=='oval' else c['PAD_SHAPE_RECT']
  if a['shape']!=shape:issue('pad_shape',**key)
  attr=c['PAD_ATTRIB_PTH'] if e['plated'] else c['PAD_ATTRIB_SMD']
  if a['attribute']!=attr:issue('pad_plating',**key)
  # *.Cu includes unused internal layers in KiCad; intersect actual two-layer stack.
  layers=[x for x in a['layers'] if x in ['F.Cu','B.Cu']]
  if layers!=(['F.Cu','B.Cu'] if e['plated'] else ['F.Cu']):issue('pad_layers',**key)
  if e['plated'] and a['drill_shape']!=c['PAD_DRILL_SHAPE_OBLONG']:issue('drill_shape',**key)
  # Square pads are rotation invariant modulo 90; oval holes must stay vertical.
  if not eq(a['rotation']% (180 if e['plated'] else 90),0):issue('pad_rotation',**key)
 holes=[a for a in inv['pads'] if a['attribute']==c['PAD_ATTRIB_NPTH']]
 if len(holes)!=1:issue('npth_count')
 else:
  h=holes[0]
  if h['ref']!='U_TX' or h['number']!='' or h['net']!='' or not pair(h['position'],[96,103]) or not pair(h['drill'],[.65,.65]) or h['shape']!=c['PAD_SHAPE_CIRCLE']:issue('npth_geometry')
 t=inv['tracks']
 if len(t)!=1 or inv['zones']!=0:issue('unexpected_copper')
 elif t[0]['kind']!='PCB_TRACK' or t[0]['net']!='GND' or t[0]['layer']!='F.Cu' or not pair(t[0]['start'],[95,100]) or not pair(t[0]['end'],[97,100]) or not eq(t[0]['width'],.2):issue('local_bond_geometry_net')
 expected_edges={((90,108),(110,108)),((110,108),(110,92)),((110,92),(90,92)),((90,92),(90,108))}
 edges={(tuple(a['start']),tuple(a['end'])) for a in inv['outline']}
 if edges!=expected_edges or len(inv['outline'])!=4 or any(a['shape']!=c['SHAPE_T_SEGMENT'] for a in inv['outline']):issue('outline')
 classes=pro['net_settings']['classes']
 if len(classes)!=1 or any(not eq(classes[0][k],v) for k,v in {'clearance':.2,'track_width':.2,'via_diameter':.6,'via_drill':.3}.items()):issue('netclass_rules')
 rules=pro['board']['design_settings']['rules']
 for k,v in {'min_hole_clearance':.2,'min_via_diameter':.6,'min_track_width':.2,'min_through_hole_diameter':.3,'min_via_annular_width':.15}.items():
  if k not in rules or not eq(rules[k],v):issue('project_rule',rule=k)
 schema=schematic_inventory(sch)
 expected_sem={'U_TX':{'1':('OUT','output'),'2':('GND','passive')},'U_RX':{'1':('IN','input'),'2':('GND','passive')}}
 for a in schema['instances']:
  ref=a['ref']
  if ref not in expected_sem:continue
  defs=[d for d in schema['definitions'] if d['lib_id']==a['lib_id']]
  if len(defs)!=1:issue('duplicate_symbol_definition',ref=ref,count=len(defs))
  for d in defs:
   got={p['number']:(p['name'],p['type']) for p in d['pins']}
   if got!=expected_sem[ref]:issue('pin_semantics_name',ref=ref,expected=expected_sem[ref],actual=got)
 return {'status':'FAIL' if errors else 'PASS','errors':errors,'pad_maps':maps,'schematic_inventory':schema,'geometry_scope':'Read-only per-object parity, source local-copper inventory and two-layer shape checks. Full post-route copper island/short/clearance reconstruction NOT ENTERED.','rule_coverage':{'compared':'explicit default netclass and five project rule fields','not_qualified':'full effective copper-edge/individual clearance rule precedence and DSN rules; no PASS claimed'},'transform':'KiCad x=100+source x, y=100-source y; component centroid retained separately from placement anchor','tolerance_mm':m.TOL}

if __name__=='__main__':
 inv=json.loads((EVIDENCE/'processes/kicad-inventory/board-inventory.json').read_text())
 pro=json.loads((EVIDENCE/'processes/smoke-conversion/smoke.kicad_pro').read_text())
 sch=(EVIDENCE/'processes/smoke-conversion/smoke.kicad_sch').read_text()
 result=compare(inv,pro,sch);result['recorded_utc']=utc()
 save(EVIDENCE/'boundary-reconciliation.json',result)
 print(json.dumps({'status':result['status'],'errors':result['errors']}))
 # A FAIL is the recorded technical outcome, not a script exception.
