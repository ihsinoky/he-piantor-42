import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, add_route, route, _seg_clear
from s28_component_route import Comp

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
BOARD = TREE / 'wmatrix.kicad_pcb'
b = pcbnew.LoadBoard(str(BOARD))
netobj = b.FindNet('H_B3_RAW')
nc = netobj.GetNetCode()
obs = Obstacles(b)
res = route(obs, (95.31, 118.09, 1), (97.06, 112.59, 1), nc, 0.10)
print('B bridge:', bool(res))
if res:
    add_route(b, netobj, 0.10, res[0], res[1])
    b.Save(str(BOARD))
else:
    pts = [(97.31, 114.09, 0), (97.75, 113.45, 0), (97.06, 112.59, 0)]
    ok = all(_seg_clear(obs, a[0], a[1], c[0], c[1], 0, nc, 0.05) for a, c in zip(pts, pts[1:]))
    print('F detour clear:', ok)
    if ok:
        add_route(b, netobj, 0.10, pts, [])
        b.Save(str(BOARD))
comp = Comp(pcbnew.LoadBoard(str(BOARD)))
print('H_B3_RAW comps:', [len(c) for c in comp.components('H_B3_RAW')])
