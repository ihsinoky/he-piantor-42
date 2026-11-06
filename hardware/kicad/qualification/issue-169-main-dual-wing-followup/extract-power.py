"""Read-only variable-width centerline diagnostic of the unqualified candidate.
No GND plane extraction / manufacturing maximum / qualification claim.
"""
from common import *
import pcbnew as p,importlib.util,inspect
label=sys.argv[1];w=E/'inspection'/label;s=json.loads((w/'snapshot.json').read_text());b=p.LoadBoard(str(w/'main.kicad_pcb'))
source=R/'hardware/kicad/qualification/issue-141-wing-power-integrity/dc-model.py'
spec=importlib.util.spec_from_file_location('dc141',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
code=inspect.getsource(m.model)
# Keep 0.1mm for short lumped object links (conservative scale), but use
# each real segment's own width for longitudinal and transverse copper.
old='resistance = rho * ((b - a) * 1e-3) / (width * THICK * 1e-6)'
assert code.count(old)==1
code=code.replace(old,"resistance = rho * ((b - a) * 1e-3) / (ts[i]['width_mm'] * width / .1 * THICK * 1e-6)")
old='edges.append((a, b, rho * length * 1e-3 / (width * THICK * 1e-6)))'
assert code.count(old)==1
code=code.replace(old,"edges.append((a, b, rho * length * 1e-3 / (min(ts[i]['width_mm'],ts[j]['width_mm']) * width / .1 * THICK * 1e-6)))")
exec(compile(code,'<variable-width-diagnostic>','exec'),m.__dict__)
layers=list(b.GetEnabledLayers().CuStack());nativepads={a.m_Uuid.AsString():a for f in b.GetFootprints() for a in f.Pads()};nativevias={a.m_Uuid.AsString():a for a in b.GetTracks() if isinstance(a,p.PCB_VIA)}
rows=[]
for temp,factor in [(20,1),(20,.8),(125,1),(125,.8)]:
 for n,source_ref,source_pins,load_ref,load_pin in [('VBUS','J1',['2','11'],'U6','12'),('V5V2','U6',['7','8'],'U5','1'),('HALL_5V','U5',['6'],'J2','1'),('HALL_5V','U5',['6'],'J3','1')]:
  ps=[dict(a) for a in s['pads'] if a['net']==n];assigned=False
  for a in ps:
   a['layers']=[l for l in layers if nativepads[a['uuid']].IsOnLayer(l)]
   if a['ref']==source_ref and a['number'] in source_pins:a['ref']='J_WING'
   elif a['ref']==load_ref and a['number']==load_pin and not assigned:a['ref']='U_H_LOAD';assigned=True
  ts=[dict(t,width_mm=t['width']) for t in s['tracks'] if t['kind']=='track' and t['net']==n]
  vs=[dict(t,diameter_mm=t['size'],drill_mm=t['drill'],layers=[l for l in layers if nativevias[t['uuid']].IsOnLayer(l)]) for t in s['tracks'] if t['kind']=='via' and t['net']==n]
  result=m.model(dict(pads=ps,tracks=ts,vias=vs),n,1.,0.,.1*factor,temp)
  rows.append(dict(net=n,source_ref=source_ref,source_pins=source_pins,load_ref=load_ref,load_pin=load_pin,temp_C=temp,width_factor=factor,positive_path_ohm=result['pins']['U_H_LOAD.'+load_pin],kcl_residual_A=result['kcl_residual_A'],pins=result['pins'],track_count=len(ts),via_count=len(vs)))
save(E/('power-extraction-'+label+'.json'),dict(utc=now(),candidate_qualified=json.loads((w/'assessment.json').read_text())['pass_acceptance'],PCB_sha256=digest(w/'main.kicad_pcb'),reference_model_sha256=digest(source),executed_model=code,rows=rows,limitations=['Positive copper only; GND plane not modelled','Variable actual widths used; conservative 0.1mm for short object links','35um copper and 20um barrel are assumptions, not manufacturing minima','Lumped centerline model, not field solver or manufactured bound']))
print('Read-only positive-copper extraction',len(rows),'cases')
