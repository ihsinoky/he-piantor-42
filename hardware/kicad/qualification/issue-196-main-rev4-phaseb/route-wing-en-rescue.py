from common import *
import shutil
w=E/'runs/auto04';w.mkdir(parents=True,exist_ok=True)
# Restart from the complete, explicit WING_EN-only rip, not a partial rescue.
for ext in ['kicad_pcb','kicad_pro']:shutil.copyfile(E/('runs/auto03/in.'+ext),w/('in.'+ext))
args=['--escalation','off','--track-width','0.1','--clearance','0.1','--same-net-pad-clearance','0.13','--via-size','0.6','--via-drill','0.3','--layers','F.Cu','In1.Cu','In2.Cu','B.Cu','--layer-costs','1','-1','1','1','--nets','WING_EN','--rip-existing-nets','HALL_5V','HALL_PWR_EN','MUX_A0','V3V3','VBUS','--no-bga-zones','J2','J3']
save(w/'conditions.json',dict(args=args,input_sha256=digest(w/'in.kicad_pcb')))
sys.exit(run('auto04',[B/'venv/bin/python3',K/'py_router/route.py',w/'in.kicad_pcb',w/'out.kicad_pcb']+args,cwd=K,timeout=1200))
