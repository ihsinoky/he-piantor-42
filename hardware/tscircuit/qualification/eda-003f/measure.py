"""Collect replay/check/connectivity metrics without rerouting or repairing."""
import hashlib
import json
from pathlib import Path
import sys

run = Path(sys.argv[1])
summary = json.loads((run/'summary.json').read_text())
generation = json.loads((run/'generation.json').read_text())
records = json.loads((run/'evidence/error-records-normalized.json').read_text())
clusters = json.loads((run/'evidence/physical-fault-clusters.json').read_text())
raw = (run/'circuit.json').read_bytes()
board = next(x for x in json.loads(raw) if x['type']=='pcb_board')
assert board['min_trace_to_pad_edge_clearance']==.2
via = [r for r in records if r['type']=='pcb_via_trace_clearance_error']
types = {'pad_pad':'pcb_pad_pad_clearance_error','pad_trace':'pcb_pad_trace_clearance_error','via_trace':'pcb_via_trace_clearance_error','trace_clearance':'pcb_trace_error','via_hole_smd_pad':'pcb_placement_error'}
metrics = {'router_settled_completed':not generation['timed_out'] and any(e['event']=='autorouting:end' for e in generation['events']) and not any(e['event']=='autorouting:error' for e in generation['events']),
 'electrically_required_unrouted_count':summary['electrically_required_unrouted_count'],
 'wrong_net_copper_components':len(summary['wrong_net_copper_components']),
 'trace_count':summary['routed_trace_count'],'via_count':summary['via_count'],
 'material_drc_record_count':len(records),
 'conservative_physical_conflict_count':clusters['independent_physical_fault_count'],
 **{k:sum(r['type']==v for r in records) for k,v in types.items()},
 'signature_0115_count':sum(abs(r['actual_minimum_spacing_mm']-.115)<=.0003 for r in via),
 'minimum_observed_via_trace_clearance_mm':min((r['actual_minimum_spacing_mm'] for r in via),default=None),
 'minimum_copper_conflict_clearance_mm':min((c['smallest_spacing_mm'] for c in clusters['clusters'] if 'pcb_placement_error' not in c['error_types']),default=None),
 'via_trace_minima_mm':[{ 'record_id':r['record_id'],'nets':[o['nets'] for o in r['objects']], 'gap_mm':r['actual_minimum_spacing_mm']} for r in via],
 'raw_sha256':hashlib.sha256(raw).hexdigest(),'elapsed_ms':generation['elapsed_ms'],
 'board_rules':board,'stock_check_counts':summary['stock_check_counts'],'result':summary['result']}
(run/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
print(json.dumps({k:v for k,v in metrics.items() if k not in ['via_trace_minima_mm','board_rules','stock_check_counts']},indent=2))
