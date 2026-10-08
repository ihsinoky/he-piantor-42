"""Read-only saved-artifact parity, library collision proof and STOP assessment."""
from process import *
import collections, importlib.util, copy
PRIOR=ROOT.parent/'eda-004c'
def module(name,file):
 spec=importlib.util.spec_from_file_location(name,PRIOR/file)
 obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj
inp=module('prior_input','check-input.py');out=module('prior_boundary','check-boundary.py')
# Imported checkers use this issue's evidence root via the local process module.
source=json.loads((PRIOR/'evidence/processes/smoke-generation-corrected/smoke.circuit.json').read_text())
intent=inp.check(source);save(EVIDENCE/'input-reconciliation.json',intent)
d=EVIDENCE/'processes/patched-smoke-conversion'
inv=json.loads((EVIDENCE/'processes/kicad-inventory/board-inventory.json').read_text())
pro=json.loads((d/'smoke.kicad_pro').read_text());sch=(d/'smoke.kicad_sch').read_text()
limited=out.compare(inv,pro,sch)
assert limited['status']=='PASS', limited['errors']
limited['status']='LIMITED_PARITY_PASS'
limited['qualification_pass']=False
save(EVIDENCE/'boundary-reconciliation.json',limited)
# All library references are checked, beyond the historical chip-only checker.
p=out.sexpr((d/'smoke.kicad_pcb').read_text())
footprints=out.children(p,'footprint')
ids=[f[1] for f in footprints]
assert ids==['tscircuit:chip','tscircuit:chip']
geometries={f['ref']:[{k:v for k,v in pad.items() if k not in ['net','ref','position','rotation']} for pad in inv['pads'] if pad['ref']==f['ref']] for f in inv['components']}
assert geometries['U_TX']!=geometries['U_RX']
upstream=Path(os.environ.get('EDA004D_WORK_DIR', '/tmp/eda004d'))/'circuit-json-to-kicad-8dee5b926f5db28800292b46b66a712c71aba055'
extract=(upstream/'lib/kicad-library/stages/ExtractFootprintsStage.ts').read_text()
assert 'if (!uniqueFootprints.has(footprintEntry.footprintName))' in extract
save(EVIDENCE/'library-assessment.json',{'status':'FAIL','configured_libraries':[],'not_configured':['tscircuit','Device','Custom'],
 'footprint_reference_map':[{'ref':f['ref'],'library_id':ids[i],'geometry':geometries[f['ref']]} for i,f in enumerate(inv['components'])],
 'finding':'Two distinct source/board footprints share one library ID. Existing ExtractFootprintsStage deduplicates by that ID, retaining first only. Adding settings cannot faithfully resolve both. No library exported or generated board changed.',
 'source_file':'lib/kicad-library/stages/ExtractFootprintsStage.ts','source_sha256':digest(upstream/'lib/kicad-library/stages/ExtractFootprintsStage.ts'),
 'source_commit':'8dee5b926f5db28800292b46b66a712c71aba055','export_execution':'NOT ENTERED; source inspection plus actual board proves identity collision; no claim of measured export failure'})
def violations(kind):
 if kind=='drc':return json.loads((EVIDENCE/'processes/kicad-pre-route-drc/pre-route-drc.json').read_text())
 return json.loads((EVIDENCE/'processes/kicad-synthetic-erc/synthetic-erc.json').read_text())
drc=violations('drc');erc=violations('erc');ev=[x for s in erc['sheets'] for x in s['violations']]
def counts(v):return dict(collections.Counter(x['type'] for x in v))
save(EVIDENCE/'pre-route-acceptance.json',{'status':'FAIL','all_conditions_pass':False,'limited_object_parity':'PASS',
 'drc_violations':counts(drc['violations']),'erc_violations':counts(ev),
 'drc_errors':sum(x['severity']=='error' for x in drc['violations']),'drc_warnings':sum(x['severity']=='warning' for x in drc['violations']),
 'erc_errors':sum(x['severity']=='error' for x in ev),'erc_warnings':sum(x['severity']=='warning' for x in ev),
 'pre_route_intentional_unconnected':len(drc['unconnected_items']),
 'shorting_items':counts(drc['violations']).get('shorting_items',0),'solder_mask_bridge':counts(drc['violations']).get('solder_mask_bridge',0),
 'meaningful_erc':'UNQUALIFIED; source output/input types preserved but logical SIG is disconnected in actual KiCad ERC',
 'real_output_output_fault_erc':None,'library_status':'FAIL: not configured; additional footprint identity collision blocks faithful configuration',
 'effective_rules':'NOT QUALIFIED: explicit default netclass/five rules match only; full precedence/DSN rules unentered',
 'schematic_pcb_parity':'NOT ENTERED; no explicit CLI parity flag was invoked',
 'measurement_tolerance_mm':1e-6,'decision_reference':'stop-decision.json'})
# Read-only fault replays use the actual patched positive artifacts. No net repairs.
results=[]
def fault(name,change,expected):
 a=copy.deepcopy(inv);b=copy.deepcopy(pro);s=change(a,b,sch) or sch
 errors=out.compare(a,b,s)['errors'];assert expected in [x['kind'] for x in errors],name
 results.append({'name':name,'detected':True,'kind':expected})
fault('duplicate GND net loss',lambda a,b,s:a['pads'][2].update(net=''),'physical_pad_net')
fault('wrong net',lambda a,b,s:a['pads'][0].update(net='GND'),'physical_pad_net')
fault('missing land',lambda a,b,s:a['pads'].pop(0) and None,'physical_pad_inventory')
fault('pad position',lambda a,b,s:a['pads'][0].update(position=[96.1,98]),'physical_pad_identity_position')
fault('component rotation',lambda a,b,s:a['components'][1].update(rotation=0),'component_transform')
fault('plating',lambda a,b,s:a['pads'][1].update(attribute=a['constants']['PAD_ATTRIB_SMD']),'pad_plating')
fault('drill',lambda a,b,s:a['pads'][1].update(drill=[.6,1.2]),'pad_drill')
fault('layer',lambda a,b,s:a['pads'][0].update(layers=['B.Cu']),'pad_layers')
fault('local copper missing',lambda a,b,s:a.update(tracks=[]),'unexpected_copper')
fault('local copper wrong net',lambda a,b,s:a['tracks'][0].update(net='SIG'),'local_bond_geometry_net')
fault('weakened clearance',lambda a,b,s:b['net_settings']['classes'][0].update(clearance=.1),'netclass_rules')
fault('output becomes passive',lambda a,b,s:s.replace('(pin output line','(pin passive line'),'pin_semantics_name')
fault('input becomes output',lambda a,b,s:s.replace('(pin input line','(pin output line'),'pin_semantics_name')
save(EVIDENCE/'checker-fault-tests.json',{'status':'PASS','count':len(results),'tests':results,
 'positive_control':'Actual patched board/project/schematic raw, with no mutation or synthetic replacement',
 'limitations':'Historical per-object checker omits footprint library identity, real schematic connectivity, rail definition duplication, full effective rules, geometric islands/short/clearance and missing-via qualification. Extended read-only assessment detects footprint identity collision. Real output/output ERC and fresh agreement NOT ENTERED.'})
print('Limited object parity PASS; pre-route FAIL; 13 independent saved-data faults detected. No qualification PASS.')
