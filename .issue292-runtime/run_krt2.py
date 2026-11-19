import subprocess, sys
from pathlib import Path
E = Path(__file__).resolve().parent
KRT = Path('/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/KiCadRoutingTools')
PY = '/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/venv/bin/python3'
SRC = E/'wmain-stripped.kicad_pcb'; OUT = E/'wmain-routed3.kicad_pcb'
NETS = ['ADC_C', 'BTN', 'FB_3V3', 'SWDCLK', 'SYS_3V3', 'VBAT_GATE_M', 'VBAT_SENSE']
POWER = ['SYS_3V3']
cmd = [PY, str(KRT/'py_router/route.py'), str(SRC), str(OUT),
       '--nets', *NETS, '--track-width', '0.1',
       '--power-nets', *POWER, '--power-nets-widths', '0.3',
       '--clearance', '0.1', '--via-size', '0.6', '--via-drill', '0.3',
       '--same-net-pad-clearance', '0.15', '--escalation', 'board']
with open(E/'krt3.log', 'w') as lf:
    r = subprocess.run(cmd, cwd=KRT, stdout=lf, stderr=subprocess.STDOUT, timeout=3000)
print('exit', r.returncode)
