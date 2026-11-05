"""Same #138 resistor method, full 2x2x2 factorial before/after, all 21 loads."""
from common import *
import importlib.util,sys,csv,itertools
spec=importlib.util.spec_from_file_location('dc_model',E/'dc-model.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
P=E/'baseline138';W=float(sys.argv[1]);results=[]
old=json.loads((P/'dc-drop-estimate.json').read_text())['results'];checks=[]
for pitch,variant in itertools.product([16,17],['before','after']):
 cell=f'KRT-{pitch}-2L-0100' if variant=='before' else f'KRT-{pitch}-2L-P{round(W*1000):04d}'
 src=(P if variant=='before' else E)/(cell+'-inventory.json');inv=json.loads(src.read_text())
 nominal=.1 if variant=='before' else W
 for current,temp,factor in itertools.product([.005,.011],[20,125],[1.,.8]):
  width=nominal*factor
  supply=m.model(inv,'HALL_5V',current,2.7e-6,width,temp)
  ground=m.model(inv,'GND',current,2.7e-6,width,temp)
  sensors=[]
  for c in sorted(inv['components'],key=lambda c:c['ref']):
   if c['value']!='DRV5055A3QDBZR':continue
   ref=c['ref'];high=supply['pins'][ref+'.1'];low=ground['pins'][ref+'.3'];drop=high+low
   sensors.append(dict(ref=ref,supply_drop_V=high,ground_rise_V=low,loop_drop_V=drop,local_supply_at_5V_V=5-drop,local_supply_at_4V75_V=4.75-drop,margin_at_4V75_V=.25-drop))
  assert len(sensors)==21
  worst=max(sensors,key=lambda s:s['loop_drop_V'])
  row=dict(cell=cell,pitch_mm=pitch,variant=variant,sensor_current_A=current,temperature_C=temp,width_factor=factor,width_mm=width,inventory_sha256=digest(src),supply=supply,ground=ground,sensors=sensors,worst_sensor=worst,max_sensor_loop_drop_V=worst['loop_drop_V'],max_ground_rise_V=max(s['ground_rise_V'] for s in sensors),required_wing_input_for_4V5_V=4.5+worst['loop_drop_V'])
  results.append(row)
  if variant=='before':
   matches=[o for o in old if o['cell']==cell and abs(o['sensor_current_A']-current)<1e-9 and o['temperature_C']==temp and abs(o['width_mm']-width)<1e-9]
   if matches:
    error=abs(matches[0]['max_sensor_loop_drop_V']-row['max_sensor_loop_drop_V']);assert error<1e-8
    checks.append(dict(cell=cell,scenario=matches[0]['scenario'],absolute_difference_V=error))
  print(cell,current,temp,round(width,5),round(worst['loop_drop_V'],6),worst['ref'],flush=True)
assert len(checks)==10
save(E/'dc-drop-estimate.json',dict(method='Issue138 centerline resistor model function copied verbatim; supplementary estimate, not guaranteed maximum',model_source_sha256=digest(P/'estimate-dc-drop.py'),model_function_unchanged=(E/'dc-model.py').read_text()==(P/'estimate-dc-drop.py').read_text().split('\ndef main():')[0],assumptions=json.loads((E/'stage0-supply.json').read_text())['assumptions'],limitations=['Main, load-switch and harness losses are outside Wing connector boundary','Ideal common GND connector sources; no harness sharing or ground offset solved','Centerline pad spreading, 20um via barrel, 35um foil and preserved manufactured junction topology are assumptions','No transient, analog-accuracy, etch-profile or guaranteed worst-case proof; 125C is resistivity sensitivity'],baseline_reproduction=checks,results=results))
with (E/'dc-comparison.csv').open('w',newline='') as f:
 fields=['pitch_mm','sensor_mA','temperature_C','width_factor','before_loop_V','after_loop_V','drop_reduction_pct','after_worst_sensor','after_ground_at_worst_V','after_max_ground_V','after_local_4V75_V','after_margin_4V75_V','after_local_5V_V','required_wing_input_V']
 writer=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');writer.writeheader()
 for b in [r for r in results if r['variant']=='before']:
  a=next(r for r in results if r['variant']=='after' and all(r[k]==b[k] for k in ['pitch_mm','sensor_current_A','temperature_C','width_factor']));w=a['worst_sensor']
  writer.writerow(dict(pitch_mm=b['pitch_mm'],sensor_mA=1000*b['sensor_current_A'],temperature_C=b['temperature_C'],width_factor=b['width_factor'],before_loop_V=b['max_sensor_loop_drop_V'],after_loop_V=a['max_sensor_loop_drop_V'],drop_reduction_pct=100*(1-a['max_sensor_loop_drop_V']/b['max_sensor_loop_drop_V']),after_worst_sensor=w['ref'],after_ground_at_worst_V=w['ground_rise_V'],after_max_ground_V=a['max_ground_rise_V'],after_local_4V75_V=w['local_supply_at_4V75_V'],after_margin_4V75_V=w['margin_at_4V75_V'],after_local_5V_V=w['local_supply_at_5V_V'],required_wing_input_V=a['required_wing_input_for_4V5_V']))
