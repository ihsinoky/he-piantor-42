"""Replace the legacy #141 Wing term with actual Rev.3 FEM terminal drops."""
from pathlib import Path
import collections,csv,hashlib,json,math
E=Path(__file__).resolve().parent;R=E.parents[3];I=.127
main=json.loads((E.parent/'issue-196-main-rev4-phaseb/resistance-summary.json').read_text())['rows'][0]
rows=[];boards=[]
for w in sorted(E.glob('wing-rev4-*')):
 if not (w/'qualification.json').exists() or not json.loads((w/'qualification.json').read_text())['pass']:continue
 data=json.loads((w/'resistance-extraction.json').read_text());assert data['board_sha256']==hashlib.sha256((w/'main.kicad_pcb').read_bytes()).hexdigest()
 assert len(data['rows'])==8
 refs=sorted({key.rsplit('.',1)[0] for r in data['rows'] for key in r['result_at_20C']['load_A']})
 cases=[]
 for width in (1.,.8):
  samples={}
  for area in (.06,.015):
   samples[area]={}
   for r in data['rows']:
    if r['track_width_factor']!=width or r['max_triangle_area_mm2']!=area:continue
    result=r['result_at_20C'];assert abs(sum(result['load_A'].values())-I)<1e-12 and result['kcl_residual_A']<1e-6
    for key in result['load_A']:
     ref=key.rsplit('.',1)[0];samples[area].setdefault(ref,0);samples[area][ref]+=result['terminal_voltage_V'][key]
  coarse=max(samples[.06].values());fine=max(samples[.015].values());delta=max(abs(samples[.06][r]-samples[.015][r]) for r in refs)/fine
  assert delta<.03,(w.name,width,'mesh needs refinement',delta)
  bound={ref:max(samples[.06][ref],samples[.015][ref]) for ref in refs};far=max(bound,key=bound.get);drop20=bound[far]
  cases.append(dict(track_width_factor=width,far_terminal=far,loop_drop_20C_V=drop20,effective_loop_20C_ohm=drop20/I,coarse_worst_drop_20C_V=coarse,fine_worst_drop_20C_V=fine,max_terminal_mesh_delta_over_worst_drop=delta))
  for temperature in (20,125):
   tf=1+.00393*(temperature-20);wingdrop=drop20*tf
   for length in sorted({124.09716799907045,200.,*[r['trial_length_mm'] for r in json.loads((E/'case/summary.json').read_text()) if 'wing-rev4-'+r['variant']==w.name]}):
    wire=1.7241e-8*length*1e-3/(.0804e-6)*tf;harness=(wire+2*.050)*(1+1/6)
    for branch in ('J2','J3'):
     main_common=2*I*(main['rail_common_loop_ohm']+.25);branchdrop=I*main['branch_loop_ohm'][branch];harnessdrop=I*harness
     vfar=5.2*.98-.050-main_common-branchdrop-harnessdrop-wingdrop
     rows.append(dict(board=w.name,main_branch=branch,actual_assembly_branch=('J2' if w.name.endswith('left') else 'J3'),temperature_C=temperature,track_width_factor=width,length_mm=length,load_A=I,wing_far_terminal=far,wing_drop_V=wingdrop,wing_effective_loop_ohm=wingdrop/I,harness_wire_ohm=wire,harness_loop_ohm=harness,harness_drop_V=harnessdrop,main_common_and_switch_drop_V=main_common,main_branch_drop_V=branchdrop,Vfar_V=vfar,margin_to_4p60_V=vfar-4.60))
 boards.append(dict(board=w.name,source_sha256=data['board_sha256'],cases=cases,max_KCL_residual_A=max(r['result_at_20C']['kcl_residual_A'] for r in data['rows'])))
worst={str(length):min((r for r in rows if abs(r['length_mm']-length)<1e-6),key=lambda r:r['Vfar_V']) for length in (124.09716799907045,200.)}
output=dict(assumptions=dict(load_A_per_wing=I,simultaneously_powered_wings=2,rail_nominal_V=5.2,rail_tolerance_fraction=.02,unmodeled_rail_budget_V=.050,U5_Ron_ohm=.25,main_corner='retained Issue196 125C / width80% Main common and branches for every row',main_common_loop_ohm=main['rail_common_loop_ohm'],main_branch_loop_ohm=main['branch_loop_ohm'],wire_copper_area_mm2=.0804,contact_ohm_each=.050,contacts_per_wire=2,return_conductors=6,copper_um=35,barrel_um=20,temperature_coefficient_per_K=.00393,width_corner='actual power track widths times0.8; native filled-plane geometry retained, as Issue196',mesh_selection='larger coarse/fine combined loop drop at each terminal; maximum over all distributed loads'),legacy_issue141_wing_drop_replaced=True,legacy_17mm_wing_drop_V=.147710145,boards=boards,worst_by_length=worst,adopted_200mm_below_4p60=worst['200.0']['Vfar_V']<4.60,limitations=['Design model, not measured operating or minimum-material voltage guarantee','Ideal pad landing contacts and equal harness return resistances; six ground terminals ideal at PCB boundary','Copper/barrel/etch minima and assembled harness/contact resistance require acceptance','125C is an analytical sensitivity corner, beyond GH catalog105C rating; it is not a qualified assembly operating temperature','Regulated rail boundary presumes upstream UDB/SH/USB/efficiency conditions meet Issue196; no new upstream power guarantee'])
(E/'power-summary.json').write_text(json.dumps(output,indent=2)+'\n')
with (E/'power-sensitivity.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
print(json.dumps(worst,indent=2))
