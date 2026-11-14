"""Unchanged baseline yardsticks with explicit DF52 contact and crimp terms.
Failed board gates remain failed; voltages are diagnostic model results.
"""
from pathlib import Path
import json,csv,itertools,hashlib
E=Path(__file__).resolve().parent;I=.127
main=json.loads((E/'resistance-summary.json').read_text())['rows'][0]
historical=json.loads((E.parent/'issue-196-main-rev4-phaseb/resistance-summary.json').read_text())['rows'][0]
legacy=json.loads((E.parent/'issue-141-wing-power-integrity/dc-drop-estimate.json').read_text())['results']
rows=[];boards=[]
def harness(temp,length,crimp):
 wire=1.7241e-8*length*.001/(.0804e-6)*(1+.00393*(temp-20))
 return wire,(wire+2*(.010+crimp))*(1+1/6)
for pitch,temp,factor,branch,crimp in itertools.product([16,17],[20,125],[1.,.8],['J2','J3'],[0.,.01,.02,.04]):
 source=next(q for q in legacy if q['variant']=='after' and q['pitch_mm']==pitch and q['temperature_C']==temp and q['width_factor']==factor and q['sensor_current_A']==.005)
 wd=source['max_sensor_loop_drop_V']*I/source['supply']['load_A'];wire,hr=harness(temp,200,crimp)
 v=5.2*.98-.05-2*I*(main['rail_common_loop_ohm']+.25)-I*(main['branch_loop_ohm'][branch]+hr)-wd
 rows.append(dict(family='main-rev7-yardstick',board='main',pitch_mm=pitch,temperature_C=temp,width_factor=factor,branch=branch,crimp_each_ohm=crimp,DF52_contact_each_ohm=.010,length_mm=200,wing_drop_V=wd,Vfar_V=v,meets_4p60=v>=4.60))
for w in sorted(E.glob('wing-rev4-*')):
 path=w/'resistance-extraction.json'
 if not path.exists():continue
 data=json.loads(path.read_text());assert len(data['rows'])==8,w.name
 assert data['board_sha256']==hashlib.sha256((w/'main.kicad_pcb').read_bytes()).hexdigest(),w.name+' stale extraction'
 refs=sorted({key.rsplit('.',1)[0] for r in data['rows'] for key in r['result_at_20C']['load_A']});cases=[]
 for factor in (1.,.8):
  samples={}
  for area in (.06,.015):
   samples[area]={}
   for r in data['rows']:
    if r['track_width_factor']!=factor or r['max_triangle_area_mm2']!=area:continue
    result=r['result_at_20C'];assert abs(sum(result['load_A'].values())-I)<1e-12
    for key in result['load_A']:
     ref=key.rsplit('.',1)[0];samples[area].setdefault(ref,0);samples[area][ref]+=result['terminal_voltage_V'][key]
  fine=max(samples[.015].values());delta=max(abs(samples[.06][ref]-samples[.015][ref]) for ref in refs)/fine
  bound={ref:max(samples[.06][ref],samples[.015][ref]) for ref in refs};far=max(bound,key=bound.get);wd=bound[far]
  cases.append(dict(width_factor=factor,far_terminal=far,drop20_V=wd,effective_loop20_ohm=wd/I,mesh_disagreement_fraction=delta,mesh_pass=delta<.03))
  for temp,branch,length,crimp in itertools.product([20,125],['J2','J3'],[124.09716799907045,200.],[0.,.01,.02,.04]):
   tf=1+.00393*(temp-20);wire,hr=harness(temp,length,crimp)
   for family,ms in [('wing-rev4-yardstick',historical),('coupled-new-candidates',main)]:
    v=5.2*.98-.05-2*I*(ms['rail_common_loop_ohm']+.25)-I*(ms['branch_loop_ohm'][branch]+hr)-wd*tf
    rows.append(dict(family=family,board=w.name,pitch_mm=int(w.name.split('-')[2][:2]),temperature_C=temp,width_factor=factor,branch=branch,crimp_each_ohm=crimp,DF52_contact_each_ohm=.010,length_mm=length,wing_drop_V=wd*tf,Vfar_V=v,meets_4p60=v>=4.60))
 boards.append(dict(board=w.name,board_sha256=data['board_sha256'],cases=cases,KCL_max_A=max(r['result_at_20C']['kcl_residual_A'] for r in data['rows']),routing_qualified=json.loads((w/'qualification.json').read_text())['routing_pass']))
worst={family:min((r for r in rows if r['family']==family and r['length_mm']==200 and r['crimp_each_ohm']==.04),key=lambda r:r['Vfar_V']) for family in sorted(set(r['family'] for r in rows))}
byboard={w['board']:min((r for r in rows if r['family']=='wing-rev4-yardstick' and r['board']==w['board'] and r['length_mm']==200 and r['crimp_each_ohm']==.04),key=lambda r:r['Vfar_V']) for w in boards}
out=dict(status='Diagnostic voltages do not override failed copper, schematic or procurement gates',assumptions=dict(load_A_each_wing=I,two_simultaneous_wings=True,rail_min_V=5.2*.98,dynamic_budget_V=.05,U5_Ron_ohm=.25,wire_minimum_area_mm2=.0804,wire_rho20_ohm_m=1.7241e-8,alpha_per_K=.00393,DF52_initial_contact_each_ohm=.010,crimp_each_ohm_conservative=.04,crimp_method_status='B2/B3 numeric crimp allowance absent from supplied summary; explicitly conservative 40mOhm assumption pending confirmation, with 0/10/20/40mOhm sweep. Not falsely represented as recovered B2/B3 data',returns=6,contacts_per_conductor=2,conductor_max_mm=200,service_reserve_included_mm=30.2,copper_um=35,barrel_um=20,temperature_corner_C=125,width_factor_corner=.8,temperature_limitation='125C numerical extrapolation, beyond DF52 +85C operating rating; not an assembly rating'),main_resistance_mOhm=dict(input_loop=1000*(main['input_positive_ohm']+main['input_GND_ohm']),common_loop=1000*main['rail_common_loop_ohm'],branches={n:1000*v for n,v in main['branch_loop_ohm'].items()}),wing_extractions=boards,worst_by_family=worst,wing_worst_by_board=byboard)
(E/'power-budget.json').write_text(json.dumps(out,indent=2)+'\n')
with (E/'power-sensitivity.csv').open('w',newline='') as f:
 cw=csv.DictWriter(f,fieldnames=list(rows[0]));cw.writeheader();cw.writerows(rows)
print(json.dumps(worst,indent=2))
