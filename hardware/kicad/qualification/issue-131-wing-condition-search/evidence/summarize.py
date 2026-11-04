"""Report exact measured outcomes; retain unexecuted cells explicitly."""
from common import *
import collections
conditions=[('KRT-16-2L-0127',.127,2),('KRT-16-2L-0100',.1,2),('KRT-16-4L-0127',.127,4),('KRT-16-4L-0100',.1,4)]
cells={};winner=None
for cell,width,layers in conditions:
 file=E/'inspection'/cell/'assessment.json'
 if file.exists():
  d=json.loads(file.read_text());cells[cell]=dict(status='PASS' if d['pass_acceptance'] else 'FAIL',width_mm=width,layers=layers,**d)
  if d['pass_acceptance']:assert winner is None;winner=cell
 else:cells[cell]=dict(status='NOT_RUN',width_mm=width,layers=layers,reason='Search stopped at first passing 16mm cell' if winner else 'Not reached',metrics={k:None for k in ['required_unconnected','wrong_net_contacts','material_violations','unexplained_transfer_changes']},measured_unconnected=None)
confirm=None
if winner:
 confirm=winner.replace('KRT-16-','KRT-17-');p=E/'inspection'/confirm/'assessment.json'
 assert p.exists()
 d=json.loads(p.read_text());cells[confirm]=dict(status='PASS' if d['pass_acceptance'] else 'FAIL',width_mm=cells[winner]['width_mm'],layers=cells[winner]['layers'],**d)
for cell,row in cells.items():
 if row['status']=='NOT_RUN':continue
 w=E/'runs'/cell;log=(E/'processes'/(cell+'-route')/'stdout').read_text()
 summary=[json.loads(line.split(': ',1)[1]) for line in log.splitlines() if line.startswith('JSON_SUMMARY_MIN: ')]
 assert len(summary)==1
 widths=json.loads((E/'inspection'/cell/'width-audit.json').read_text());physical=json.loads((E/'inspection'/cell/'physical-audit.json').read_text())
 record=json.loads((E/'processes'/(cell+'-route')/'record.json').read_text())
 save(w/'report.json',dict(assessment=row,router_self_report=summary[0],independent_width_audit=widths,physical_audit=physical,elapsed_seconds=record['elapsed_seconds'],route_exit_code=record['exit_code']))
save(E/'assessment.json',dict(utc=now(),status='CONDITION_FOUND' if winner else 'ALL_CONDITIONS_FAILED',first_passing_16mm_cell=winner,confirmation_cell=confirm,cells=cells,ordered_search=True,stop_at_first_pass=True,one_route_per_executed_cell=True))
print(json.dumps({k:dict(status=v['status'],unconnected=v['measured_unconnected'],metrics=v['metrics']) for k,v in cells.items()},indent=2))
