from common import *
import itertools,math,io,csv
summaries=json.loads((E/'resistance-summary.json').read_text())['rows']
# No efficiency guarantee is invented. Retain all design/stress separations.
r=.001+25e-6*100
lo=.8*.99*(1+54900*(1-r)/(10000*(1+r)))-100e-9*54900*(1+r)
hi=.8*1.01*(1+54900*(1+r)/(10000*(1-r)))+100e-9*54900*(1+r)
assert lo>5.2*.98 and hi<5.2*1.02
rows=[]
for s in summaries:
 for vin,eta,wing,rail in itertools.product([4.50,5.0,5.25],[.75,.8,.85,.9,.95],[.127,.2310081,.278],[5.2,5.304,5.354]):
  R=s['input_positive_ohm']+s['input_GND_ohm'];other=.110;P=2*wing*rail/eta;term=vin-R*other;disc=term*term-4*R*P
  cv=(term+math.sqrt(disc))/2;ci=P/cv;total=ci+other
  far={k:5.2*.98-.05-2*wing*(s['rail_common_loop_ohm']+.25)-wing*s['branch_loop_ohm'][k]-(.019305+.147710145)*wing/.127 for k in ['J2','J3']}
  rows.append(dict(seed=s['label'],load_class='design' if wing==.127 else 'stress-only',connector_V=vin,efficiency_assumption=eta,Wing_A=wing,rail_V=rail,converter_V=cv,converter_A=ci,Main_other_allocation_A=other,total_USB_A=total,input_loop_ohm=R,USB_500mA_calculation=total<=.5,conditional_farthest_J2_V=far['J2'],conditional_farthest_J3_V=far['J3']))
stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows);(E/'connector-current-sensitivity.csv').write_text(stream.getvalue())
save(E/'power-budget.json',dict(utc=now(),PCB_qualified=True,current_guarantee_established=False,feedback_nominal_V=.8*(1+54900/10000),feedback_corner_V=[lo,hi],feedback_assumptions='FB ±1% forced PWM; R initial ±0.1% and ±25ppm/K over 100K; FB leakage100nA; no long-term drift claim',USB_connector_V=[4.50,5.25],USB_configured_allowance_A=.5,design_Wing_A=.127,Main_other_allocated_A=.110,efficiency_lower_bound_guaranteed=False,simulated_cases=len(rows),current_equation='converter_V + input_loop_ohm * total_USB_A = connector_V; converter_A * converter_V * efficiency = 2*Wing_A*rail_V',farthest_formula='Target rail minimum5.096 minus50mV dynamic allowance minus Main common loop @2*I, assumed0.25ohm U5 Ron @2*I, branch loop @I, and inherited harness/17mm-Wing drops scaled from127mA',farthest_is_conditional=True,not_established=['Converter efficiency minimum across input/load/PVT','Main 110mA actual maximum in all relevant USB/firmware states','Dynamic ±50mV, cold start, overshoot, reverse feeding, EMI/ADC settling','USB configured/reset/suspend permission firmware and verification','Finished copper/plating/stackup minima and actual return-contact current split','Manufacturing acceptance; prototype electrical validation']))
