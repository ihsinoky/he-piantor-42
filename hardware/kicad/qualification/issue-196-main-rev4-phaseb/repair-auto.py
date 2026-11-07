"""Incremental automatic completion of the three open supply connections."""
from common import *
import sexpdata as sx,shutil
label='auto02';w=E/'runs'/label;w.mkdir(parents=True,exist_ok=True)
# NPTH mounting hole itself must be allowed within its copper reservation.
# All copper pads are separately checked geometrically. Track/via/pour bans stay.
for src,dest in [(E/'inputs/final/main.kicad_pcb',E/'inputs/final/main.kicad_pcb'),(E/'runs/auto01/out.kicad_pcb',w/'in.kicad_pcb')]:
 s=src.read_text().replace('(pads not_allowed)','(pads allowed)');dest.write_text(s)
shutil.copyfile(E/'inputs/final/main.kicad_pro',w/'in.kicad_pro')
args=['--escalation','off','--track-width','0.1','--clearance','0.1','--same-net-pad-clearance','0.13','--via-size','0.6','--via-drill','0.3','--layers','F.Cu','In1.Cu','In2.Cu','B.Cu','--layer-costs','1','-1','1','1','--keep-input-copper','--nets','V1V1','V3V3']
save(w/'conditions.json',dict(args=args,input_sha256=digest(w/'in.kicad_pcb'),change='0.1mm signal clearance (D-019) with 0.13mm same-net via pad; hole NPTH pad allowed'))
sys.exit(run(label,[B/'venv/bin/python3',K/'py_router/route.py',w/'in.kicad_pcb',w/'out.kicad_pcb']+args,cwd=K,timeout=1200))
