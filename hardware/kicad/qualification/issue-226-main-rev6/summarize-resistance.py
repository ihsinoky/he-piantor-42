"""Report actual independent observations; failed qualification never becomes zero."""
from common import *
import csv,io,itertools,math
summaries=[];attempts=[]
for label in ['final']:
 a=json.loads((E/'inspection'/label/'assessment.json').read_text());g=json.loads((E/'inspection'/label/'connectivity.json').read_text())
 attempts.append(dict(label=label,qualified=a['pass_acceptance'],nets_checked=g['nets_checked'],measured_four_metrics=dict(required_unconnected=g['required_unconnected'],wrong_net_contacts=g['wrong_net_contacts'],material_violations=a['metrics']['material_violations'],unexplained_transfer_changes=a['metrics']['unexplained_transfer_changes']),conditional_qualification_metrics=a['metrics'],source_project_used=True))
 ext=json.loads((E/('power-extraction-'+label+'.json')).read_text());corner=[x for x in ext['rows'] if x['temp_C']==125 and x['width_factor']==.8]
 rv=next(x['positive_path_ohm'] for x in corner if x['net']=='VBUS');rr=next(x['positive_path_ohm'] for x in corner if x['net']=='V5V2');j2=next(x for x in corner if x['net']=='HALL_5V' and x['load_ref']=='J2');j3=next(x for x in corner if x['net']=='HALL_5V' and x['load_ref']=='J3');hc=(j2['pins']['J3.1']+j3['pins']['J2.1'])/2
 ground=json.loads((E/('ground-extraction-'+label+'.json')).read_text());fine=next(x for x in ground['rows'] if x['track_width_factor']==.8 and x['max_triangle_area_mm2']==.0075);scale=1+.00393*105
 def av(row,ref):return sum(v for k,v in row['terminal_voltage_V'].items() if k.startswith(ref+'.'))/6
 returns=fine['results_at_20C'];one,two,both=returns['output_returns'];gc=(av(one,'J3')+av(two,'J2'))/2*scale;gin=sum(returns['input_return']['terminal_voltage_V'][k]*v for k,v in returns['input_return']['load_A'].items())*scale
 branch_positive=dict(J2=j2['positive_path_ohm']-hc,J3=j3['positive_path_ohm']-hc);branch_ground=dict(J2=av(one,'J2')*scale-gc,J3=av(two,'J3')*scale-gc)
 summary=dict(label=label,board_sha256=digest(E/'inspection'/label/'main.kicad_pcb'),qualified=a['pass_acceptance'],corner='125C, actual positive widths -20%; actual GND tracks -20%, native filled plane/spokes; assumed 35um sheet / 20um barrel',input_positive_ohm=rv,input_GND_ohm=gin,rail_common_positive_ohm=rr+hc,rail_common_GND_ohm=gc,rail_common_loop_ohm=rr+hc+gc,branch_positive_ohm=branch_positive,branch_GND_ohm=branch_ground,branch_loop_ohm={k:branch_positive[k]+branch_ground[k] for k in branch_positive},all_loop_targets_met_in_model=rr+hc+gc<=.05 and all(branch_positive[k]+branch_ground[k]<=.05 for k in branch_positive),operating_board_guarantee=False,limitations='Actual routed copper extraction with assumed materials. Native GND plane/spoke etch tolerances, finished material minima and operating power performance are not established.')
 summaries.append(summary)
save(E/'resistance-summary.json',dict(utc=now(),model_only=True,rows=summaries))

print('Final copper resistance summary saved')
