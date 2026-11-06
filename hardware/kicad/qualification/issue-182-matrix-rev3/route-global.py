from pathlib import Path
import sys,shutil,json
R=Path.cwd();E=R/'hardware/kicad/qualification/issue-182-matrix-rev3';sys.path.insert(0,str(E));from common import *
cell=sys.argv[1] if len(sys.argv)>1 else 'GLOBAL-01'
w=E/'runs'/cell;w.mkdir(parents=True,exist_ok=False)
source=E/'cell-inputs'/cell
for ext in ['kicad_pcb','kicad_pro']:shutil.copyfile(source/('main.'+ext),w/('in.'+ext))
shutil.copyfile(source/'fp-lib-table',w/'fp-lib-table')
options=['--track-width','0.1','--power-nets','HALL_5V','GND','--power-nets-widths','0.3','0.3','--escalation','off','--clearance','0.1','--via-size','0.6','--via-drill','0.3','--same-net-pad-clearance','0.1']
if cell=='GLOBAL-02':options+=['--no-power-tap-neckdown','--ordering','original']
if cell=='GLOBAL-03':options+=['--no-power-tap-neckdown','--grid-step','0.05']
save(w/'launch.json',dict(utc=now(),options=options,input_sha256=digest(w/'in.kicad_pcb'),project_sha256=digest(w/'in.kicad_pro'),timeout_seconds=1800))
run(cell+'-readback',[T/'venv/bin/python3',E/'read-effective.py',w/'effective.json',w/'in.kicad_pcb',*options],timeout=120)
c=json.loads((w/'effective.json').read_text())['grid_route_config']
assert c['track_width']==.1 and c['clearance']==.1 and c['via_size']==.6 and c['via_drill']==.3 and c['same_net_pad_clearance']==.1
assert sorted(c['power_net_widths'].values())==[.3,.3]
run(cell+'-route',[T/'venv/bin/python3','py_router/route.py',w/'in.kicad_pcb',w/'out.kicad_pcb',*options],timeout=1800,cwd=T/'KiCadRoutingTools')
print('Saved global route',cell,flush=True)
