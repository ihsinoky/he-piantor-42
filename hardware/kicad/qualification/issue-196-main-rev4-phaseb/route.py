from common import *
import shutil
w=E/'runs/auto01';w.mkdir(parents=True,exist_ok=True)
for ext in ['kicad_pcb','kicad_pro']:shutil.copyfile(E/('inputs/final/main.'+ext),w/('in.'+ext))
args=['--escalation','off','--track-width','0.1','--clearance','0.13','--same-net-pad-clearance','0.13','--via-size','0.6','--via-drill','0.3','--layers','F.Cu','In1.Cu','In2.Cu','B.Cu','--layer-costs','1','-1','1','1','--power-nets','VBUS','V5V2','HALL_5V','--power-nets-widths','0.8','1.2','1.2']
save(w/'conditions.json',dict(args=args,input_sha256=digest(w/'in.kicad_pcb')))
sys.exit(run('auto01',[B/'venv/bin/python3',K/'py_router/route.py',w/'in.kicad_pcb',w/'out.kicad_pcb']+args,cwd=K,timeout=2400))
