from common import *
import collections
rows={}
for label in ['smoke-cell1','main-cell1']:
 w=E/'inspection'/label/'krt';lines=(E/'processes'/(label+'-krt-route')/'stdout').read_text().splitlines();structured={}
 for line in lines:
  for tag in ['JSON_SUMMARY','JSON_SUMMARY_MIN','JSON_REGRADE','JSON_ORACLE','VIA_IN_PAD_JSON','PROJECT_WRITES_JSON']:
   if line.startswith(tag+': '):structured.setdefault(tag,[]).append(json.loads(line[len(tag)+2:]))
 save(w/'router-structured-log.json',structured)
 independent=json.loads((w/'independent.json').read_text());record=json.loads((E/'processes'/(label+'-krt-route')/'record.json').read_text())
 rows[label]=dict(independent=independent,process=record,stop_reason='CLI normal completion; final written-board regrade 37/37 nets complete' if label.startswith('main') else 'CLI normal completion; independent smoke accepted',router_summary=structured['JSON_SUMMARY_MIN'][-1],all_project_differences=independent['output_project_changes'])
save(E/'assessment.json',dict(utc=utc(),completed=True,confirmed_minimum_in_declared_search_order='cell1: 4-layer, width/clearance 0.10mm, via 0.60/0.30mm, escalation off',global_minimum_proven=False,executed_main_cells=['cell1'],not_executed=['cell2','cell3','cell4'],rows=rows))
save(E/'manufacturing-sources.json',dict(accessed_utc=utc(),sources=[dict(url='https://jlcpcb.com/capabilities/pcb-capabilities/',title='JLCPCB Rigid PCB Capabilities',relevant_sections=['Traces: minimum width/space (1 oz), multilayer 0.09/0.09mm; 2 oz multilayer 0.15/0.15mm','Drilling: preferred minimum via hole 0.2mm; extra cost for 0.1/0.15mm holes, or 0.2/0.25mm holes with diameter below 0.45mm','Thickness: includes 1.2mm FR4'],interpretation='0.10/0.10mm within listed 1oz multilayer capability. 0.45/0.20mm is not below the stated diameter threshold; price not quoted. Final PCB DFM and via-in-pad process not established by this routing qualification.')]))
