"""Route wmain with KiCadRoutingTools (repo-proven router, #263/#275 machinery)."""
import subprocess, sys
from pathlib import Path
E = Path(__file__).resolve().parent
W = E.parent
KRT = Path('/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/KiCadRoutingTools')
PY = sys.argv[1]  # python with numpy/scipy/shapely + pcbnew NOT required by route.py
BOARD = W/'hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb'
OUT = E/'wmain-routed.kicad_pcb'
POWER = ['SYS_3V3', 'HALL_3V3', 'VIN_IN', 'VBAT', 'VBUS', 'PAD_3V3', 'SW_A', 'SW_B']
import re
txt = BOARD.read_text()
nets = sorted(set(re.findall(r'\(net \d+ "([A-Z0-9_]+)"\)', txt))) 
nets = [n for n in nets if n and n != 'GND']
print('nets to route:', len(nets))
cmd = [PY, str(KRT/'py_router/route.py'), str(BOARD), str(OUT),
       '--nets', *nets,
       '--track-width', '0.1',
       '--power-nets', *POWER,
       '--power-nets-widths', *(['0.3'] * len(POWER)),
       '--clearance', '0.1', '--via-size', '0.6', '--via-drill', '0.3',
       '--same-net-pad-clearance', '0.15', '--escalation', 'board']
with open(E/'krt.log', 'w') as lf:
    r = subprocess.run(cmd, cwd=KRT, stdout=lf, stderr=subprocess.STDOUT, timeout=3000)
print('KRT exit:', r.returncode, 'out exists:', OUT.exists())
