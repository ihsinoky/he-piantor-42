"""One fixed KRT route invocation; no retries or adaptive parameter changes."""
from common import *
import sys,shutil
cell,board,width,layers=sys.argv[1:];width=float(width);layers=int(layers)
assert json.loads((E/'equivalence-gate.json').read_text())['pass_equivalence']
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,11,5,0,43,54,tzinfo=datetime.timezone.utc)
source=E/'inputs'/board;derived=E/'cell-inputs'/cell;derived.mkdir(parents=True,exist_ok=False)
for f,h in json.loads((E/'stage0-frozen-hashes.json').read_text())[board].items():assert digest(source/f)==h
for f in source.iterdir():shutil.copy2(f,derived/f.name)
pro=json.loads((derived/'main.kicad_pro').read_text());pro['board']['design_settings']['rules'].update(min_clearance=width,min_track_width=width)
for nc in pro['net_settings']['classes']:nc.update(clearance=width,track_width=width,via_diameter=.6,via_drill=.3)
save(derived/'main.kicad_pro',pro)
assert layers==2 # Four-layer derivation is added only if reached by the ordered search.
assert digest(derived/'main.kicad_pcb')==digest(source/'main.kicad_pcb')
condition=dict(cell=cell,board=board,width_mm=width,clearance_mm=width,layers=layers,via_diameter_mm=.6,via_drill_mm=.3,thickness_mm=1.2,escalation='off',single_run=True)
save(derived/'condition.json',condition)
save(derived/'hashes.json',{f.name:digest(f) for f in derived.iterdir() if f.is_file()})
w=E/'runs'/cell;w.mkdir(parents=True,exist_ok=False)
for ext in ['kicad_pcb','kicad_pro']:shutil.copy2(derived/('main.'+ext),w/('in.'+ext))
shutil.copy2(derived/'fp-lib-table',w/'fp-lib-table')
options=['--escalation','off','--track-width',str(width),'--clearance',str(width),'--via-size','0.6','--via-drill','0.3']
save(w/'launch.json',dict(**condition,utc=now(),input_sha256=digest(w/'in.kicad_pcb'),project_sha256=digest(w/'in.kicad_pro'),options=options))
assert run(cell+'-readback',[T/'venv/bin/python3',E/'read-effective.py',w/'effective.json',w/'in.kicad_pcb',*options],timeout=120)==0
rc=run(cell+'-route',[T/'venv/bin/python3','py_router/route.py',w/'in.kicad_pcb',w/'out.kicad_pcb',*options],T/'KiCadRoutingTools',1800)
save(w/'execution.json',dict(exit_code=rc,input_unchanged=digest(w/'in.kicad_pcb')==digest(derived/'main.kicad_pcb'),project_unchanged=digest(w/'in.kicad_pro')==digest(derived/'main.kicad_pro'),outputs={f.name:digest(f) for f in w.iterdir() if f.is_file()}))
assert run(cell+'-inspection',['/usr/bin/python3',E/'inspect-cell.py',cell,board,'KRT'],timeout=1200)==0
