"""In-memory adversarial replay only. Never edits raw boards or launches EDA tools."""
import copy,importlib.util,json
from pathlib import Path
from process import ROOT,EVIDENCE,save

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
inp=load('inp',ROOT/'check-input.py');out=load('out',ROOT/'check-boundary.py')
raw=json.loads((EVIDENCE/'processes/smoke-generation-corrected/smoke.circuit.json').read_text())
assert inp.check(raw)['status']=='PASS'
results=[]

def input_fault(name,mutate):
 data=copy.deepcopy(raw);mutate(data)
 try:inp.check(data)
 except (AssertionError,KeyError):results.append({'name':name,'detected':True});return
 raise AssertionError('fault escaped: '+name)
def first(data,kind):return next(x for x in data if x['type']==kind)
input_fault('missing physical pad',lambda d:d.remove(first(d,'pcb_smtpad')))
input_fault('wrong net false source label',lambda d:first(d,'source_trace').update(connected_source_net_ids=['source_net_1']))
input_fault('local copper displaced',lambda d:first(d,'pcb_trace')['route'][1].update(x=-7))
input_fault('local copper layer loss',lambda d:first(d,'pcb_trace')['route'][1].update(layer='bottom'))
input_fault('pad shape',lambda d:first(d,'pcb_smtpad').update(shape='circle'))
input_fault('oval drill size',lambda d:first(d,'pcb_plated_hole').update(hole_width=.9))
input_fault('duplicate land omitted',lambda d:d.remove(first(d,'pcb_plated_hole')))
input_fault('duplicate internal connection omitted',lambda d:d.remove(first(d,'source_component_internal_connection')))
input_fault('clearance rule lowered',lambda d:first(d,'pcb_board').update(min_pad_edge_to_pad_edge_clearance=.1))
input_fault('extra global stock copper',lambda d:d.append({'type':'pcb_via'}))
input_fault('output-output circuit fault',lambda d:next(x for x in d if x['type']=='source_port' and x['name']=='IN').update(is_input=False,is_output=True))
# A metadata-only positive parity control. It is not a corrected KiCad board,
# not converter output, and not a transport/routing result.
inv=json.loads((EVIDENCE/'processes/kicad-inventory/board-inventory.json').read_text())
pro=json.loads((EVIDENCE/'processes/smoke-conversion/smoke.kicad_pro').read_text())
for p in inv['pads']:
 if p['ref']=='U_TX' and p['position']==[97,100]:p['net']='GND'
sch='''(kicad_sch (lib_symbols
 (symbol "synthetic:TX" (symbol "pins" (pin output line (name "OUT") (number "1")) (pin passive line (name "GND") (number "2"))))
 (symbol "synthetic:RX" (symbol "pins" (pin input line (name "IN") (number "1")) (pin passive line (name "GND") (number "2")))))
 (symbol (lib_id "synthetic:TX") (property "Reference" "U_TX"))
 (symbol (lib_id "synthetic:RX") (property "Reference" "U_RX")))'''
assert out.compare(inv,pro,sch)['status']=='PASS'

def boundary_fault(name,mutate,kind):
 data=copy.deepcopy(inv);project=copy.deepcopy(pro);text=mutate(data,project,sch) or sch
 errors=out.compare(data,project,text)['errors']
 assert kind in [e['kind'] for e in errors], name
 results.append({'name':name,'detected':True,'error_kind':kind})
boundary_fault('KiCad duplicate GND land net absent',lambda d,p,s:d['pads'][2].update(net=''),'physical_pad_net')
boundary_fault('KiCad wrong-net label',lambda d,p,s:d['pads'][0].update(net='GND'),'physical_pad_net')
boundary_fault('KiCad missing physical pad',lambda d,p,s:d['pads'].pop(0) and None,'physical_pad_inventory')
boundary_fault('KiCad plating changed',lambda d,p,s:d['pads'][1].update(attribute=d['constants']['PAD_ATTRIB_SMD']),'pad_plating')
boundary_fault('KiCad pad transform shifted',lambda d,p,s:d['pads'][0].update(position=[96.1,98]),'physical_pad_identity_position')
boundary_fault('KiCad component rotation changed',lambda d,p,s:d['components'][1].update(rotation=0),'component_transform')
boundary_fault('KiCad layer changed',lambda d,p,s:d['pads'][0].update(layers=['B.Cu']),'pad_layers')
boundary_fault('KiCad oval drill changed',lambda d,p,s:d['pads'][1].update(drill=[.6,1.2]),'pad_drill')
boundary_fault('KiCad pad shape changed',lambda d,p,s:d['pads'][1].update(shape=0),'pad_shape')
boundary_fault('KiCad board thickness changed',lambda d,p,s:d.update(thickness_mm=1.6),'stack')
boundary_fault('KiCad outline changed',lambda d,p,s:d['outline'][0].update(end=[111,108]),'outline')
boundary_fault('KiCad local bond missing',lambda d,p,s:d.update(tracks=[]),'unexpected_copper')
boundary_fault('KiCad local bond wrong net',lambda d,p,s:d['tracks'][0].update(net='SIG'),'local_bond_geometry_net')
boundary_fault('KiCad rule weakened',lambda d,p,s:p['net_settings']['classes'][0].update(clearance=.1),'netclass_rules')
boundary_fault('KiCad all-passive semantic loss',lambda d,p,s:s.replace('pin output','pin passive'),'pin_semantics_name')
save(EVIDENCE/'checker-fault-tests.json',{'status':'PASS','tests':results,'count':len(results),'positive_controls':['source-derived input matches fixed synthetic intent','metadata-only KiCad parity control with distinct typed synthetic definitions'],'limitations':'Read-only mutation replay; no KiCad board repaired/regenerated. Not full copper-island/short/clearance geometry or missing-via fault qualification; those are NOT ENTERED. No real-device/Main ERC claim.'})
print(f'{len(results)} in-memory checker faults detected')
