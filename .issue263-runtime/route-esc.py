import subprocess, sys, time
from pathlib import Path
E = Path('/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation')
RT = '/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/KiCadRoutingTools/py_router/route.py'
PY = sys.executable
OPTS = ['--track-width', '0.1', '--power-nets', 'HALL_5V', 'GND', '--power-nets-widths', '0.3', '0.3',
        '--clearance', '0.1', '--via-size', '0.6', '--via-drill', '0.3', '--same-net-pad-clearance', '0.15']
for name in sys.argv[1:]:
    w = E / name
    t0 = time.time()
    r = subprocess.run([PY, RT, str(w / 'respin-in.kicad_pcb'), str(w / 'routed-esc.kicad_pcb'),
                        '--escalation', 'board', *OPTS],
                       stdout=open(w / 'route-esc.log', 'w'), stderr=subprocess.STDOUT)
    print(name, 'esc exit', r.returncode, f'{time.time()-t0:.0f}s', flush=True)
print('done')
