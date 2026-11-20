import subprocess, sys
from pathlib import Path
E = Path(__file__).resolve().parent
KRT = Path('/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/KiCadRoutingTools')
PY = '/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/venv/bin/python3'
net, src, out = sys.argv[1], sys.argv[2], sys.argv[3]
cmd = [PY, str(KRT/'py_router/route.py'), str(E/src), str(E/out),
       '--nets', net, '--track-width', '0.1',
       '--clearance', '0.1', '--via-size', '0.6', '--via-drill', '0.3',
       '--same-net-pad-clearance', '0.15', '--escalation', 'board',
       '--layers', 'F.Cu', 'In2.Cu', 'B.Cu']
with open(E/f'krt-one-{net}.log', 'w') as lf:
    r = subprocess.run(cmd, cwd=KRT, stdout=lf, stderr=subprocess.STDOUT, timeout=1200)
print(net, 'exit', r.returncode)
