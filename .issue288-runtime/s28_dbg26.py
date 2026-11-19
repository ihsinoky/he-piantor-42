import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
import s24_router
from s24_router import Obstacles, route

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
obs = Obstacles(b)
tests = [
    ('H_B3_RAW', (134.25, 72.3, 0), (130.5, 73.0, 0)),
    ('H_C5_RAW', (151.25, 106.3, 0), (150.0, 112.0, 0)),
    ('EN_C', (151.25, 107.7, 0), (151.0, 91.2, 0)),
    ('EN_C', (151.25, 107.7, 0), (151.25, 90.7, 0)),
]
for net, pa, pb in tests:
    nc = b.FindNet(net).GetNetCode()
    r1 = route(obs, pa, pb, nc, 0.10)
    if not r1:
        s24_router.GRID = 0.125
        r1 = route(obs, pa, pb, nc, 0.10)
        s24_router.GRID = 0.25
    print(net, pa, '->', pb, ':', 'OK' if r1 else 'FAIL')
