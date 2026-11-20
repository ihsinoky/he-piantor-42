import math, sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, _seg_clear

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
obs = Obstacles(b)
nc = b.FindNet('H_A0_RAW').GetNetCode()
segs = [((79.9, 121.7), (80.3, 121.35)), ((80.3, 121.35), (80.45, 120.75))]
for (a, c) in segs:
    print('seg', a, c, 'clear:', _seg_clear(obs, a[0], a[1], c[0], c[1], 0, nc, 0.05))
    steps = max(2, int(math.hypot(c[0] - a[0], c[1] - a[1]) / 0.1))
    for k in range(steps + 1):
        t = k / steps
        x, y = a[0] + (c[0] - a[0]) * t, a[1] + (c[1] - a[1]) * t
        if obs.blocked(x, y, 0, nc, 0.05):
            print('   blocked sample', (round(x, 3), round(y, 3)))
