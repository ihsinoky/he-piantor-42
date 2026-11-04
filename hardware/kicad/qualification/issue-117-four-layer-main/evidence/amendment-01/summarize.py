"""Summarize actual saved outputs; never runs a router."""
from helpers import *
import re,collections
summary={}
for router in ['fab','krt']:
 w=A/'inspection/main'/router;raw=A/'runs/main'/router
 independent=json.loads((w/'independent.json').read_text());physical=independent['physical']
 launch=json.loads((E/'processes'/('amend01-main-'+router+'-route')/'record.json').read_text())
 drc=json.loads((w/'drc.json').read_text())
 networks=collections.Counter();endpoints=[]
 for item in drc['unconnected_items']:
  nets=sorted(set(n for obj in item['items'] for n in re.findall(r'\[([^\]]+)\]',obj['description'])))
  for n in nets:networks[n]+=1
  endpoints.append(dict(nets=nets,**item))
 save(w/'unconnected-net-endpoints.json',dict(count=len(endpoints),net_count=len(networks),counts_by_net=dict(sorted(networks.items())),items=endpoints))
 project=json.loads((w/'transfer-diff.json').read_text())['output_project_changes']
 # Quantify numerical rule-floor changes, distinguishing additions from decreases.
 floors=[d for d in project if d['path'].startswith('/board/design_settings/rules/') or d['path'].startswith('/net_settings/')]
 relaxed=[d for d in floors if isinstance(d['before'],(int,float)) and isinstance(d['after'],(int,float)) and d['after']<d['before']]
 stop=json.loads((raw/'result.json').read_text())['report']['stoppedBy'] if router=='fab' else 'Fixed CLI completed its routing, rescue, reconciliation and re-grade; exit 0 with open nets'
 router_claim=json.loads((raw/'check-drc-after.json').read_text())['counts'] if router=='fab' else None
 summary[router]=dict(status='PASS' if independent['pass_acceptance'] else 'FIXED_CONDITION_FAIL',main_runs=1,independent_metrics=independent['metrics'],unconnected_count=independent['measured_unconnected_count'],unconnected_network_count=len(networks),unconnected_counts_by_net=dict(sorted(networks.items())),unconnected_net_endpoint_list_file=str((w/'unconnected-net-endpoints.json').relative_to(E)),width_distribution=physical['track_width_mm_counts'],via_distribution=physical['via_diameter_drill_mm_counts'],tracks_per_layer=physical['tracks_per_layer'],plane_connections=json.loads((w/'plane-connectivity.json').read_text()),elapsed_seconds=launch['elapsed_seconds'],start_utc=launch['start_utc'],end_utc=launch['end_utc'],exit_code=launch['exit_code'],timed_out=launch['timed_out'],stop_reason=stop,router_claim_counts=router_claim,DRC_type_counts=independent['drc_type_counts'],raw_material_DRC_count=independent['raw_material_DRC_count'],output_project_changes=project,existing_rule_floor_decreases=relaxed,output_project_rule_floor_changes=floors,plane_role_pass=independent['plane_role_pass'],unexplained_change_raw_count=independent['unexplained_change_raw_count'],raw_output_sha256=sha(raw/'out.kicad_pcb'),refilled_output_sha256=sha(w/'main.kicad_pcb'))
 assert not relaxed
save(A/'assessment.json',dict(utc=utc(),status='PASS' if all(v['status']=='PASS' for v in summary.values()) else 'FIXED_CONDITION_FAIL',stage0=json.loads((A/'smoke-gate.json').read_text()),stage1=summary,stage1_total_route_runs=2,stage1_restarts=0,smoke_route_runs_per_candidate=2,smoke_preparation_attempts=2,prior_stop_history='../assessment.json and report-before-amendment.md',main_rebuilt=False,wing='Prior run 2 analytical outlook retained without re-investigation; no layout inputs consumed',D012_modified=False))
print(json.dumps(summary,indent=2))
