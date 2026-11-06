"""Bounded D-021 routes. No width/layer/clearance or escalation relaxation."""
from common import *
import sys,shutil,datetime
cell=sys.argv[1] if len(sys.argv)>1 else 'KRT-M1-01'
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(json.loads((E/'start.json').read_text())['deadline_utc'])
assert cell in ['KRT-M1-01','KRT-M1-02','KRT-M1-03']
source=E/'inputs/m1-matrix18-16-17mm';derived=E/'cell-inputs'/cell
shutil.copytree(source,derived)
save(derived/'condition.json',dict(width_mm=.3,signal_width_mm=.1,clearance_mm=.1,layers=2,thickness_mm=1.2,via_diameter_mm=.6,via_drill_mm=.3,escalation='off'))
w=E/'runs'/cell;w.mkdir(parents=True,exist_ok=False)
for ext in ['kicad_pcb','kicad_pro']:shutil.copyfile(derived/('main.'+ext),w/('in.'+ext))
shutil.copyfile(derived/'fp-lib-table',w/'fp-lib-table')
options=['--track-width','0.1','--power-nets','HALL_5V','GND','--power-nets-widths','0.3','0.3','--escalation','off','--clearance','0.1','--via-size','0.6','--via-drill','0.3']
save(w/'launch.json',dict(utc=now(),options=options,input_sha256=digest(w/'in.kicad_pcb'),project_sha256=digest(w/'in.kicad_pro'),timeout_seconds=1800))
run(cell+'-readback',[T/'venv/bin/python3',E/'read-effective.py',w/'effective.json',w/'in.kicad_pcb',*options],timeout=120)
effective=json.loads((w/'effective.json').read_text());c=effective['grid_route_config']
assert c['track_width']==.1 and c['clearance']==.1 and c['via_size']==.6 and c['via_drill']==.3
assert c['power_net_widths'] and sorted(c['power_net_widths'].values())==[.3,.3] and not c['net_track_widths']
run(cell+'-route',[T/'venv/bin/python3','py_router/route.py',w/'in.kicad_pcb',w/'out.kicad_pcb',*options],timeout=1800,cwd=T/'KiCadRoutingTools')
run(cell+'-inspect',['/usr/bin/python3',E/'inspect-cell.py',cell,'m1-matrix18-16-17mm','KRT'],timeout=1200)
run(cell+'-physical',['/usr/bin/python3',E/'physical-audit.py',cell],timeout=120)
