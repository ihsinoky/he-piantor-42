"""Record the terminal K1 result without entering post-safety physical comparison.
Usage: python3 summarize-ab.py A_RUN B_RUN EVIDENCE_DIR
"""
import gzip
import hashlib
import json
from pathlib import Path
import sys

here=Path(__file__).resolve().parent
a_run,b_run,out=map(Path,sys.argv[1:])
out.mkdir(parents=True,exist_ok=True)
def write(name,value): (out/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
def sha(raw): return hashlib.sha256(raw).hexdigest()
a=json.loads((a_run/'metrics.json').read_text())
s=json.loads((b_run/'summary.json').read_text());g=json.loads((b_run/'generation.json').read_text())
raw=(b_run/'circuit.json').read_bytes();d=json.loads(raw)
material=[e for e in d if e['type'].endswith('_error')]
assert sorted((e['type'],e.get('message')) for e in material)==sorted((e['type'],e.get('message')) for e in s['stock_material_diagnostics']), 'Generated material diagnostics and stock replay disagree'
via=[e for e in material if e['type']=='pcb_via_trace_clearance_error']
board=next(e for e in d if e['type']=='pcb_board')
assert board==a['board_rules'], 'Board/rules changed'
assert len(s['wrong_net_copper_components'])==2 and s['electrically_required_unrouted_count']==0
b={'router_settled_completed':not g['timed_out'] and any(e['event']=='autorouting:end' for e in g['events']),
'electrically_required_unrouted_count':s['electrically_required_unrouted_count'],'wrong_net_copper_components':len(s['wrong_net_copper_components']),
'wrong_net_component_nets':s['wrong_net_copper_components'],'trace_count':s['routed_trace_count'],'via_count':s['via_count'],
'material_drc_record_count':len(material),'conservative_physical_conflict_count':None,
**{k:sum(e['type']==v for e in material) for k,v in {'pad_pad':'pcb_pad_pad_clearance_error','pad_trace':'pcb_pad_trace_clearance_error','via_trace':'pcb_via_trace_clearance_error','trace_clearance':'pcb_trace_error','via_hole_smd_pad':'pcb_placement_error'}.items()},
'signature_0115_count':sum(abs(e['actual_clearance']-.115)<=.0003 for e in via),
'minimum_observed_via_trace_clearance_mm':min(e['actual_clearance'] for e in via),
'via_trace_minima_mm':[{'id':e['pcb_via_trace_clearance_error_id'],'via':e['pcb_via_id'],'trace':e['pcb_trace_id'],'gap_mm':e['actual_clearance']} for e in via],
'raw_sha256':sha(raw),'elapsed_ms':g['elapsed_ms'],'board_rules':board,'stock_check_counts':s['stock_check_counts'],'result':s['result'],
'safety_kill_gate':{'first_trigger':'K1','wrong_net_regression':True,'action':'STOP; no additional routing, patching, physical-conflict comparison or confirmation'},
'physical_conflict_count_status':'NOT ENTERED after K1; raw error records are not interchangeable with conservative physical conflicts',
'diagnostics_generated_match_stock_replay':True}
write('intervention-b',b)
keys=['electrically_required_unrouted_count','wrong_net_copper_components','material_drc_record_count','conservative_physical_conflict_count','pad_pad','pad_trace','via_trace','trace_clearance','via_hole_smd_pad','signature_0115_count','trace_count','via_count','minimum_observed_via_trace_clearance_mm']
comparison={'metrics':{k:{'A':a[k],'B':b[k],'delta_B_minus_A':None if b[k] is None else b[k]-a[k]} for k in keys},'control_comparable':True,'safety_result':'K1_FAILED','physical_comparison':'NOT ENTERED: B is electrically unsafe','physical_conflicts_removed':None,'new_physical_conflicts':None,'wrong_net_components_introduced':2,'migration_assessment':'NOT ASSESSED after K1; disappearance of the signature and lower raw DRC count do not establish improvement','classification':'INTERVENTION_UNSAFE_REGRESSION'}
write('ab-comparison',comparison)
write('conflict-diff',{'status':'NOT ENTERED','reason':'K1 wrong-net STOP precedes direct physical comparison; B is not electrically safe','A_accepted_clusters_reproduced':54,'B_conservative_physical_conflicts':None,'REMOVED':None,'RETAINED':None,'NEW':None,'MOVED/LIKELY_MIGRATED':None,'UNMATCHED':None,'removed_percent':None,'net_physical_conflict_reduction':None,'new_wrong_net_components':b['wrong_net_component_nets'],'migration':'No clearance-fix claim is made; two new multi-net copper components are a material electrical regression.'})
write('reproducibility',{'status':'NOT PERFORMED','B_generation_processes':1,'reason':'K1 wrong-net regression; B is not potentially positive. No second run is authorized.','A_control':'Byte-identical to accepted EDA-003C and all 54 EDA-003D cluster identities identical.'})
(out/'raw').mkdir(exist_ok=True)
(out/'raw/intervention-b.circuit.json.gz').write_bytes(gzip.compress(raw,mtime=0))
write('raw/artifact-manifest',{'intervention-b.circuit.json.gz':{'uncompressed_sha256':sha(raw),'compressed_sha256':sha((out/'raw/intervention-b.circuit.json.gz').read_bytes()),'uncompressed_size_bytes':len(raw)},'control_A':{'accepted_file_repository_relative':'hardware/tscircuit/qualification/eda-003c/evidence/raw/latest-main.circuit.json.gz','uncompressed_sha256':a['raw_sha256'],'byte_identical':True}})
for name,run in [('a',a_run),('b',b_run)]:
    for filename in ['generation.json','summary.json']:
        (out/(name+'-'+filename)).write_bytes((run/filename).read_bytes())
(out/'b-material-records.json').write_text(json.dumps(material,indent=2)+'\n')
print(json.dumps(comparison,indent=2))
