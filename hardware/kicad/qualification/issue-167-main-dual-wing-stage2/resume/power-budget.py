"""New connector-referenced budget: engineering calculations, never sign-off.
Separates component-guaranteed DC tolerance from allocations needing validation.
"""
from common import *
import math,itertools,csv
usb=dict(host_min_V=4.75,cable_vbus_max_drop_V=.125,cable_gnd_max_drop_V=.125,connector_min_V=4.50,connector_max_V=5.25,configured_permission_A=.5)
assert abs(usb['host_min_V']-usb['cable_vbus_max_drop_V']-usb['cable_gnd_max_drop_V']-usb['connector_min_V'])<1e-12
# Independent endpoint enumeration: 0.1% initial plus 25ppm/K * max100K.
r=.001+25e-6*100;lo=.8*.99*(1+55000*(1-r)/(10000*(1+r)))-100e-9*55000*(1+r);hi=.8*1.01*(1+55000*(1+r)/(10000*(1-r)))+100e-9*55000*(1+r)
assert lo>5.2*.98 and hi<5.2*1.02
others=[dict(load='RP2040 incl. internal linear VREG, USB/ADC and external logic switching',estimate_max_A=.080,basis='RP2040 datasheet Table637 maximum-average Popcorn DVDD16.6mA+IOVDD35.5mA+USB2mA=54.1mA; reserve25.9mA. Workload-specific engineering allocation; not a silicon max or verified133MHz ceiling.'),dict(load='W25Q16JV flash',estimate_max_A=.025,basis='Manufacturer current limit envelope used for read/program/erase planning; system PVT/active-I/O supply validation remains open.'),dict(load='LDO quiescent, USB/CC/ESD/pullups/pulldowns and other auxiliary loads',estimate_max_A=.005,basis='5mA engineering reserve. AP2112 Iq80uA, ESD/pullups/control not individually qualified at every state.')]
other=sum(x['estimate_max_A'] for x in others);assert abs(other-.110)<1e-12
extract=json.loads((E/'power-extraction-local.json').read_text());corner=[x for x in extract['rows'] if x['temp_C']==125 and x['width_factor']==.8]
rv=next(x['positive_path_ohm'] for x in corner if x['net']=='VBUS');rr=next(x['positive_path_ohm'] for x in corner if x['net']=='V5V2')
a=next(x for x in corner if x['net']=='HALL_5V' and x['load_ref']=='J2');b=next(x for x in corner if x['net']=='HALL_5V' and x['load_ref']=='J3');rc=(a['pins']['J3.1']+b['pins']['J2.1'])/2
branch={'J2':a['positive_path_ohm']-rc,'J3':b['positive_path_ohm']-rc}
rows=[]
for vin,eta,ground,wing,rail in itertools.product([4.50,5.0,5.25],[.75,.8,.85,.9,.95],[0,.025,.05],[.127,.2310081,.278],[5.2,5.304,5.354]):
 # Lump all other loads into the same extracted path as conservative allocation,
 # then solve the constant-power converter equation. GND is a sensitivity only.
 resistance=rv+ground;power=2*wing*rail/eta;term=vin-resistance*other;disc=term*term-4*resistance*power
 conv_v=(term+math.sqrt(disc))/2;conv_i=power/conv_v;total=conv_i+other
 assert abs(conv_v+resistance*total-vin)<1e-12 and abs(conv_v*conv_i-power)<1e-12
 rows.append(dict(connector_V=vin,efficiency_assumption=eta,input_positive_extracted_ohm=rv,GND_loop_assumption_ohm=ground,Wing_A=wing,rail_V=rail,converter_V=conv_v,converter_A=conv_i,Main_other_allocated_A=other,total_USB_A=total,within_500mA_arithmetic=total<=.5,scope='design' if wing==.127 else 'stress-only'))
with (E/'connector-current-sensitivity.csv').open('w',newline='') as f:
 c=csv.DictWriter(f,fieldnames=rows[0].keys(),lineterminator="\n");c.writeheader();c.writerows(rows)
# Re-evaluate the inherited worst Wing drop with actual POSITIVE Main paths.
# No invented GND extraction: keep three explicit ground-loss sensitivities.
old=list(csv.DictReader((E.parent/'conditional-downstream.csv').open()))
# Use independently documented #141/#165 worst corner 17mm Wing 147.710145mV at127mA,
# plus representative100mm harness/contact loop drop19.305mV. Both scale with current.
volts=[]
for iw,gd in itertools.product([.127,.2310081,.278],[0,.025,.05]):
 mainpos=2*iw*(rr+rc)+iw*max(branch.values())
 v=5.2*.98-.05-2*iw*.25-mainpos-gd-(.147710145+.019305)*iw/.127
 volts.append(dict(Wing_A=iw,positive_Main_drop_V=mainpos,additional_GND_drop_assumption_V=gd,conditional_farthest_V=v,target_V=4.60,scope='design' if iw==.127 else 'stress-only',qualified=False))
save(E/'power-budget.json',dict(utc=now(),qualified=False,USB=usb,DC_feedback_tolerance=dict(nominal_V=5.2,resistor_initial_fraction=.001,resistor_drift_ppm_per_K=25,max_delta_K=100,FB_accuracy_fraction=.01,FB_leakage_max_A=100e-9,calculated_min_V=lo,calculated_max_V=hi,DC_target_min_V=5.096,DC_target_max_V=5.304,arithmetic_within_target=True,limitations='Precision resistor MPN/thermal matching, feedback routing pickup and system DC behaviour not qualified'),ripple_transient=dict(per_side_budget_V=.05,verified=False,reason='No validated capacitor effective C / ESR / loop transient / prototype waveform. Allocation is not a proof.'),other_Main_maximum_estimate=others,other_Main_allocated_A=other,current_sensitivity_rows=len(rows),efficiency_min_guaranteed=False,current_guarantee_established=False,input_voltage_range_arithmetic_established=True,positive_extracted_corner_ohm=dict(VBUS_to_U6=rv,V5V2_to_U5=rr,HALL_common=rc,branches=branch),Main_common_loop_target_ohm=.05,Main_common_positive_alone_ohm=rr+rc,Main_common_target_not_met_in_model=rr+rc>.05,conditional_downstream=volts,not_established=['Actual GND loop resistance','80% efficiency lower bound across PVT and forced-PWM operation','RP2040 workload maximum and USB configuration/suspend firmware','50mV dynamic rail budget and selected capacitors','Normal operation with broken V1V1/V3V3 nets','Farthest-sensor design guarantee']))
print('Connector budget and',len(rows),'arithmetic cases saved; qualification remains false')
