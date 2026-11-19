import subprocess
from pathlib import Path
E = Path(__file__).resolve().parent
KRT = Path('/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/KiCadRoutingTools')
PY = '/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/venv/bin/python3'
cmd = [PY, str(KRT/'py_router/route.py'), str(E/'wmain-v4-stripped3.kicad_pcb'), str(E/'wmain-v4-routed4.kicad_pcb'),
       '--nets', 'SWDIO', 'VBAT_GATE_M', 'PAD_DR',
       '--track-width', '0.1',
       '--clearance', '0.1', '--via-size', '0.6', '--via-drill', '0.3',
       '--same-net-pad-clearance', '0.15', '--escalation', 'board',
       '--layers', 'F.Cu', 'In2.Cu', 'B.Cu']
with open(E/'krt-v4d.log', 'w') as lf:
    r = subprocess.run(cmd, cwd=KRT, stdout=lf, stderr=subprocess.STDOUT, timeout=3000)
print('exit', r.returncode)
