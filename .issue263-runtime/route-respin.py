"""R2: KRT route of Wing respin inputs (respin-in -> routed), D-021 opts.
Usage: route-respin.py [variant ...] [--esc]"""
from pathlib import Path
import subprocess, concurrent.futures, time, json, os, sys
E = Path('/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation')
T = Path('/home/hatch/workspace/projects/he-piantor-boards/.issue263-runtime')
KRT = Path('/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/KiCadRoutingTools')
esc = '--esc' in sys.argv
names = [a for a in sys.argv[1:] if not a.startswith('--')] or \
        ['wing-rev5-16mm-left', 'wing-rev5-16mm-right', 'wing-rev5-17mm-right']
opts = ['--track-width', '0.1', '--power-nets', 'HALL_5V', 'GND', '--power-nets-widths', '0.3', '0.3',
        '--escalation', 'board' if esc else 'off', '--clearance', '0.1', '--via-size', '0.6',
        '--via-drill', '0.3', '--same-net-pad-clearance', '0.15']

def run(name):
    w = E / name
    start = time.time()
    cmd = [str(T / 'run'), '/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/venv/bin/python3',
           str(KRT / 'py_router/route.py'), str(w / 'respin-in.kicad_pcb'), str(w / 'routed.kicad_pcb'), *opts]
    logname = 'route-respin-esc.log' if esc else 'route-respin.log'
    with (w / logname).open('w') as f:
        try:
            r = subprocess.run(cmd, cwd=KRT, stdout=f, stderr=subprocess.STDOUT, timeout=2400)
            code = r.returncode
        except subprocess.TimeoutExpired:
            code = 124
    print(name, 'esc' if esc else 'std', code, f'{time.time()-start:.0f}s', flush=True)

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    list(pool.map(run, names))
print('done')
