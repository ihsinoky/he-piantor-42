"""Compare freshly extracted Rev5/Rev6 with identical materials/solver corners."""
from common import *
import math,csv
V=E.parent/'issue-221-main-rev5'
def extract(label,base):
 pos=json.loads((base/f'power-extraction-{label}.json').read_text());ground=json.loads((base/f'ground-extraction-{label}.json').read_text())
 corner=[x for x in pos['rows'] if x['temp_C']==125 and x['width_factor']==.8]
 rv=next(x['positive_path_ohm'] for x in corner if x['net']=='VBUS')
 rr=next(x['positive_path_ohm'] for x in corner if x['net']=='V5V2')
 j2=next(x for x in corner if x['net']=='HALL_5V' and x['load_ref']=='J2');j3=next(x for x in corner if x['net']=='HALL_5V' and x['load_ref']=='J3');hc=(j2['pins']['J3.1']+j3['pins']['J2.1'])/2
 def av(row,ref):return sum(v for k,v in row['terminal_voltage_V'].items() if k.startswith(ref+'.'))/6
 scale=1+.00393*105
 def values(row):
  r=row['results_at_20C'];one,two,_=r['output_returns'];gc=(av(one,'J3')+av(two,'J2'))/2*scale
  gin=sum(r['input_return']['terminal_voltage_V'][k]*v for k,v in r['input_return']['load_A'].items())*scale
  return dict(input_positive_ohm=rv,input_GND_ohm=gin,input_loop_ohm=rv+gin,rail_common_loop_ohm=rr+hc+gc,branch_J2_loop_ohm=j2['positive_path_ohm']-hc+av(one,'J2')*scale-gc,branch_J3_loop_ohm=j3['positive_path_ohm']-hc+av(two,'J3')*scale-gc)
 fine=next(q for q in ground['rows'] if q['max_triangle_area_mm2']==.0075 and q['track_width_factor']==.8)
 coarse=next(q for q in ground['rows'] if q['max_triangle_area_mm2']==.03 and q['track_width_factor']==.8)
 a,b=values(coarse),values(fine);convergence={k:abs(a[k]-b[k]) for k in a}
 return dict(PCB_sha256=pos['PCB_sha256'],values=b,coarse_to_fine_abs_ohm=convergence,max_ground_KCL_residual_A=max(r['kcl_residual_A'] for row in ground['rows'] for r in [row['results_at_20C']['input_return'],*row['results_at_20C']['output_returns']]),positive_cases=len(pos['rows']),ground_cases=len(ground['rows']))
a,b=extract('final',V),extract('final',E);delta={k:b['values'][k]-a['values'][k] for k in a['values']}
old=json.loads((V/'resistance-summary.json').read_text())['rows'][0]
assert abs(a['values']['input_positive_ohm']-old['input_positive_ohm'])<1e-10
assert abs(a['values']['input_GND_ohm']-old['input_GND_ohm'])<1e-7
assert all(b['values'][k]<.05 for k in ['input_loop_ohm','rail_common_loop_ohm','branch_J2_loop_ohm','branch_J3_loop_ohm'])
oldbudget=json.loads((V/'power-budget.json').read_text());newbudget=json.loads((E/'power-budget.json').read_text());up=[]
for x,y in zip(oldbudget['upstream_sensitivity'],newbudget['upstream_sensitivity']):
 assert x['efficiency_assumption']==y['efficiency_assumption'] and x['Fly_PTC_EZmate_contacts_reservation_ohm']==y['Fly_PTC_EZmate_contacts_reservation_ohm']
 assert x['within_configured_500mA']==y['within_configured_500mA']
 up.append(dict(efficiency=y['efficiency_assumption'],upstream_reservation_ohm=y['Fly_PTC_EZmate_contacts_reservation_ohm'],old_converter_V=x['converter_V'],new_converter_V=y['converter_V'],delta_converter_V=y['converter_V']-x['converter_V'],old_total_USB_A=x['total_USB_A'],new_total_USB_A=y['total_USB_A'],delta_total_USB_A=y['total_USB_A']-x['total_USB_A'],classification_unchanged=True,within_500mA=y['within_configured_500mA']))
worst=newbudget['six_return_worst']['farthest_V'];assert worst>=4.60 and round(worst,3)==round(oldbudget['six_return_worst']['farthest_V'],3)
save(E/'power-impact.json',dict(pass_model_comparison=True,model_only=True,corner='125C; actual track widths x0.8; 35um copper, 20um barrel, assumed z=[0,.2,1,1.2]mm; Rev6 freshly extracted with Rev5 scripts; Rev5 saved baseline extraction hash-linked via PCB',rev5=a,rev6=b,delta_ohm=delta,input_loop_meets_50mOhm_model=True,regulated_far_point_V=worst,rev5_regulated_far_point_V=oldbudget['six_return_worst']['farthest_V'],downstream_conclusion_unchanged=True,upstream_sensitivity=up,max_extra_input_drop_at_500mA_V=.5*delta['input_loop_ohm'],upstream_500mA_classification_changes=0,limitations=['No measured finished Fly/cable/contact/fuse resistance or converter efficiency; retained sweeps are sensitivity reservations','75% efficiency sensitivities already fail USB500mA in Rev5 and still fail in Rev6; no unconditional upstream power guarantee','Nominal-geometry/assumed-material extraction, not manufactured minima or operating hardware guarantee','GH each conductor200mm >=0.0804mm2, contacts50mOhm, six returns and 127mA per Wing are retained constraints; first-power cable polarity measurement mandatory']))
print('Power comparison PASS',a['values'],b['values'],'delta',delta)
