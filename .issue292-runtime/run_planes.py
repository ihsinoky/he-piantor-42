import subprocess
from pathlib import Path
E = Path(__file__).resolve().parent
KRT = Path('/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/KiCadRoutingTools')
PY = '/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/venv/bin/python3'
import os
env = dict(os.environ, PYTHONPATH=f"{KRT/'py_router'}:{KRT/'rust_router'}")
cmd = [PY, str(KRT/'py_router/route_planes.py'), str(E/'wmain-v4-final.kicad_pcb'),
       '--output', str(E/'wmain-v4-planes2.kicad_pcb'), '--overwrite',
       '--nets', 'GND', '--plane-layers', 'In1.Cu',
       '--via-size', '0.6', '--via-drill', '0.3', '--track-width', '0.3',
       '--clearance', '0.1']
with open(E/'krt-planes.log', 'w') as lf:
    r = subprocess.run(cmd, cwd=KRT/'py_router', stdout=lf, stderr=subprocess.STDOUT, timeout=3000, env=env)
print('exit', r.returncode)
