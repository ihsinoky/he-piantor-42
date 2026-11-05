"""Single fixed-class route, CLI widths pinned to the same project classes."""
from common import *
import sys,shutil,copy
cell,board,width=sys.argv[1:];width=float(width)
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(json.loads((E/'start.json').read_text())['deadline_utc'])
prev=E.parent/'issue-131-wing-condition-search/evidence'
assert json.loads((prev/'equivalence-gate.json').read_text())['pass_equivalence']
source=prev/'inputs'/board;derived=E/'cell-inputs'/cell;derived.mkdir(parents=True,exist_ok=False)
for f,h in json.loads((prev/'stage0-frozen-hashes.json').read_text())[board].items():assert digest(source/f)==h
for f in source.iterdir():shutil.copyfile(f,derived/f.name)
pro=json.loads((derived/'main.kicad_pro').read_text());original=copy.deepcopy(pro)
pro['board']['design_settings']['rules'].update(min_clearance=.1,min_track_width=.1)
assert len(pro['net_settings']['classes'])==1
signal=pro['net_settings']['classes'][0];signal.update(clearance=.1,track_width=.1,via_diameter=.6,via_drill=.3)
power=copy.deepcopy(signal);power.update(name='Power',track_width=width,priority=0)
pro['net_settings']['classes'].append(power)
pro['net_settings']['netclass_patterns']=[dict(netclass='Power',pattern=n) for n in ['HALL_5V','GND']]
save(derived/'main.kicad_pro',pro)
# Only relocate the library lookup to the byte-identical copied library.
(derived/'fp-lib-table').write_text((source/'fp-lib-table').read_text().replace('issue-131-wing-condition-search/evidence','issue-141-wing-power-integrity'))
assert digest(derived/'main.kicad_pcb')==digest(source/'main.kicad_pcb')
condition=dict(cell=cell,board=board,width_mm=width,signal_width_mm=.1,clearance_mm=.1,layers=2,via_diameter_mm=.6,via_drill_mm=.3,thickness_mm=1.2,escalation='off',single_run=True)
save(derived/'condition.json',condition)
save(derived/'derivation.json',dict(source=str(source.relative_to(R)),source_project=original,derived_project=pro,pcb_byte_identical=True,source_pcb_sha256=digest(source/'main.kicad_pcb'),source_gate_sha256=digest(prev/'equivalence-gate.json'),library_lookup_only_relocated=True))
save(derived/'hashes.json',{f.name:digest(f) for f in derived.iterdir() if f.is_file()})
w=E/'runs'/cell;w.mkdir(parents=True,exist_ok=False)
for ext in ['kicad_pcb','kicad_pro']:shutil.copyfile(derived/('main.'+ext),w/('in.'+ext))
shutil.copyfile(derived/'fp-lib-table',w/'fp-lib-table')
options=['--track-width','0.1','--power-nets','HALL_5V','GND','--power-nets-widths',str(width),str(width),'--escalation','off','--clearance','0.1','--via-size','0.6','--via-drill','0.3']
save(w/'launch.json',dict(**condition,utc=now(),input_sha256=digest(w/'in.kicad_pcb'),project_sha256=digest(w/'in.kicad_pro'),options=options,width_source='project netclasses plus matching CLI signal and power width pins'))
assert run(cell+'-readback',[T/'venv/bin/python3',E/'read-effective.py',w/'effective.json',w/'in.kicad_pcb',*options],timeout=120)==0
readback=json.loads((w/'effective.json').read_text());config=readback['grid_route_config']
assert config['track_width']==.1 and config['clearance']==.1
assert not config['net_track_widths']
assert sorted(config['power_net_widths'].values())==[width,width],config['power_net_widths']
assert config['via_size']==.6 and config['via_drill']==.3
rc=run(cell+'-route',[T/'venv/bin/python3','py_router/route.py',w/'in.kicad_pcb',w/'out.kicad_pcb',*options],T/'KiCadRoutingTools',1800)
save(w/'execution.json',dict(exit_code=rc,input_unchanged=digest(w/'in.kicad_pcb')==digest(derived/'main.kicad_pcb'),project_unchanged=digest(w/'in.kicad_pro')==digest(derived/'main.kicad_pro'),outputs={f.name:digest(f) for f in w.iterdir() if f.is_file()}))
assert run(cell+'-inspection',['/usr/bin/python3',E/'inspect-cell.py',cell,board,'KRT'],timeout=1200)==0
shutil.copyfile(E/'inspection'/cell/'assessment.json',w/'report.json')
