"""200mm GH conductors are explicit path lengths, not a scaled 100mm loss constant."""
from common import *
import itertools,math,csv,io
s=json.loads((E/'resistance-summary.json').read_text())['rows'][0]
# #165 conductor material/area and contact model, with actual 0.200m per wire.
# One forward conductor; six individual 0.200m return conductors in parallel.
rho20=1.7241e-8;area_m2=.0804e-6;length_m=.200;alpha=.00393
wing=json.loads((E.parent/'issue-141-wing-power-integrity/dc-drop-estimate.json').read_text())['results']
rows=[]
for pitch,temp,factor,current,returns in itertools.product([16,17],[20,125],[1.,.8],[.127,.2310081,.278],[6,1]):
 source=next(q for q in wing if q['variant']=='after' and q['pitch_mm']==pitch and q['temperature_C']==temp and q['width_factor']==factor and q['sensor_current_A']==.005)
 wdrop=source['max_sensor_loop_drop_V']*current/source['supply']['load_A']
 wire=rho20*length_m/area_m2*(1+alpha*(temp-20));contact=.05
 harness=(wire+2*contact)*(1+1/returns)
 # Preserve the qualified board corner even at cooler cable temperature.
 for branch in ['J2','J3']:
  far=5.2*.98-.05-2*current*(s['rail_common_loop_ohm']+.25)-current*(s['branch_loop_ohm'][branch]+harness)-wdrop
  rows.append(dict(pitch_mm=pitch,temperature_C=temp,width_factor=factor,Wing_A=current,branch=branch,return_conductors=returns,each_conductor_path_m=length_m,wire_ohm=wire,contact_each_ohm=contact,harness_loop_ohm=harness,wing_drop_V=wdrop,farthest_V=far,design=current==.127,meets_4p60=far>=4.60))
stream=io.StringIO();cw=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n');cw.writeheader();cw.writerows(rows);(E/'power-sensitivity.csv').write_text(stream.getvalue())
design=[r for r in rows if r['design'] and r['return_conductors']==6];worst=min(design,key=lambda q:q['farthest_V']);single=min([r for r in rows if r['design'] and r['return_conductors']==1],key=lambda q:q['farthest_V'])
# The previous #175 VBUS boundary is now at Main J4. Fly/EZmate upstream losses
# are separately reserved, never counted as regulated downstream cable loss.
upstream=[]
for eta in [.75,.8,.85,.9,.95]:
 for upstream_r in [.25,.5,1.]:
  R=upstream_r+s['input_positive_ohm']+s['input_GND_ohm'];P=2*.127*5.304/eta;vin=4.75;other=.110;term=vin-R*other;cv=(term+math.sqrt(term*term-4*R*P))/2;ci=P/cv;upstream.append(dict(USB_V=vin,efficiency_assumption=eta,Fly_PTC_EZmate_contacts_reservation_ohm=upstream_r,main_input_loop_ohm=s['input_positive_ohm']+s['input_GND_ohm'],converter_V=cv,total_USB_A=ci+other,within_configured_500mA=ci+other<=.5))
assert worst['farthest_V']>=4.60 and s['all_loop_targets_met_in_model']
save(E/'power-budget.json',dict(board_sha256=s['board_sha256'],common_and_branches_meet_50mOhm=True,design_Wing_A=.127,GH_length_m=.2,GH_wire_area_mm2=.0804,GH_gauge_model='AWG28 equivalent from #165; finished harness must meet this minimum area/resistance assumption',rho20_ohm_m=rho20,alpha_per_K=alpha,conductor_formula='rho20 * 0.200m / 0.0804mm2 * (1+0.00393*(T-20)); one forward plus six full-length parallel return wires; 50mOhm each contact at both ends of each wire',six_return_worst=worst,single_return_sensitivity=single,regulated_rail_min_V=5.096,dynamic_allocation_V=.05,common_switch_Ron_ohm=.25,upstream_sensitivity=upstream,upstream_actual_resistance_guaranteed=False,limitations=['DC design model, not measured board or supplier resistance guarantee','200mm is finished electrical conductor length per wire including routing/bend slack; 156.341mm planar route plus 43.659mm bend/length allowance; no chord-length shortcut','AWG28 equivalent is a procurement constraint: unknown or thinner finished harness cannot inherit this pass','Fly fuse hot resistance, EZmate cable gauge/length and contact losses require assembly acceptance. Upstream resistance sweep is a reservation, not a measured guarantee','Converter efficiency, 110mA Main allocation, startup, USB permissions, rail transient and ADC noise require prototype validation','Legacy #141 Wing copper is the #165/#175 load-model input; future routed Wing Rev.2 needs new extraction']))
print('200mm harness design worst',worst['farthest_V'],'single-return sensitivity',single['farthest_V'])
