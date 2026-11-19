import subprocess
from pathlib import Path
E = Path(__file__).resolve().parent
KRT = Path('/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/KiCadRoutingTools')
PY = '/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/venv/bin/python3'
cmd = [PY, str(KRT/'py_router/route.py'), str(E/'wmain-v2-stripped.kicad_pcb'), str(E/'wmain-v2-routed3.kicad_pcb'),
       '--nets', 'ADC_C', 'BTN', 'MUX_A0', 'SYS_3V3', 'VBAT_SENSE',
       '--track-width', '0.1', '--power-nets', 'SYS_3V3', '--power-nets-widths', '0.3',
       '--clearance', '0.1', '--via-size', '0.6', '--via-drill', '0.3',
       '--same-net-pad-clearance', '0.15', '--escalation', 'board']
with open(E/'krt-v2c.log', 'w') as lf:
    r = subprocess.run(cmd, cwd=KRT, stdout=lf, stderr=subprocess.STDOUT, timeout=3000)
print('exit', r.returncode)
