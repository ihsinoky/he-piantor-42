import subprocess, sys, time
from pathlib import Path
E = Path('/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation')
RT = '/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/KiCadRoutingTools/py_router/route.py'
OPTS = ['--track-width', '0.1', '--power-nets', 'HALL_5V', 'GND', '--power-nets-widths', '0.3', '0.3',
        '--escalation', 'off', '--clearance', '0.1', '--via-size', '0.6', '--via-drill', '0.3',
        '--same-net-pad-clearance', '0.15']
w = E / sys.argv[1]
src, dst = sys.argv[2], sys.argv[3]
t0 = time.time()
r = subprocess.run([sys.executable, RT, str(w / src), str(w / dst), *OPTS],
                   stdout=open(w / 'route-rerun.log', 'w'), stderr=subprocess.STDOUT)
print(sys.argv[1], 'rerun exit', r.returncode, f'{time.time()-t0:.0f}s')
