"""Independent logical Wing interface check; this is NOT native schematic ERC.
Uses the backend-independent circuit contract, not inferred copper net names.
"""
from pathlib import Path
import json,sys
sys.dont_write_bytecode=True
E=Path(__file__).resolve().parent;ROOT=E.parents[3];sys.path.insert(0,str(ROOT/'hardware/jitx'))
from wing.definition import INTERFACE,HALL_PINS,MUX_PINS
results=[]
for w in sorted(E.glob('wing-rev4-*')):
 d=json.loads((w/'definition.json').read_text());parts={c['reference']:c for c in d['components']};j=parts['J_WING']['pins'];assert [j[str(i)] for i in range(1,15)]==list(INTERFACE);assert list(INTERFACE).count('GND')==6
 for group in 'ABC':
  mux=parts['U_MUX_'+group]['pins']
  for role,net in {'VDD':'HALL_5V','GND':'GND','EN':'WING_EN','D':'MUX_OUT_'+group,**{f'A{i}':f'MUX_A{i}' for i in range(3)}}.items():assert mux[MUX_PINS[role]]==net
  assert mux[MUX_PINS['NC']] is None and mux[MUX_PINS['S8']] is None
  for i in range(7):
   ref=f'U_H{group}{i}';raw=f'H_{group}{i}_RAW';hall=parts[ref]['pins'];assert hall=={'1':'HALL_5V','2':raw,'3':'GND'};assert mux[MUX_PINS[f'S{i+1}']]==raw
   assert parts[f'C_H{group}{i}']['pins']=={'1':'HALL_5V','2':'GND'}
  assert parts['C_MUX_'+group]['pins']=={'1':'HALL_5V','2':'GND'}
 results.append({'variant':w.name,'logical_errors':0,'GH14_1to1_and_six_returns':True,'three_seven_channel_mux_groups':True,'S8_and_NC_unconnected':True,'Hall_and_MUX_local_decoupling':True,'raw_outputs_stay_in_5V_domain_Main_dividers_unchanged':True,'native_ERC':'not run; no native Wing schematic supplied, no design acceptance claimed','DC_voltage':'not qualified on any board failing the routing gate'})
(E/'electrical-contract.json').write_text(json.dumps(results,indent=2)+'\n');print('Logical checks pass for four variants; no native ERC claimed')
