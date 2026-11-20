import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, add_route, route, _seg_clear

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
BOARD = TREE / 'wmatrix.kicad_pcb'
b = pcbnew.LoadBoard(str(BOARD))
netobj = b.FindNet('H_A0_RAW')
nc = netobj.GetNetCode()
obs = Obstacles(b)
ok_f = _seg_clear(obs, 79.9, 121.7, 80.3, 122.0, 0, nc, 0.05)
v1 = not (obs.blocked(80.3, 122.0, 0, nc, 0.30, via=True) or obs.blocked(80.3, 122.0, 1, nc, 0.30, via=True))
v2 = not (obs.blocked(80.65, 120.2, 0, nc, 0.30, via=True) or obs.blocked(80.65, 120.2, 1, nc, 0.30, via=True))
print('F hop clear:', ok_f, 'via S legal:', v1, 'via N legal:', v2)
if ok_f and v1 and v2:
    add_route(b, netobj, 0.10, [(79.9, 121.7, 0), (80.3, 122.0, 0)], [(80.3, 122.0), (80.65, 120.2)])
    b.Save(str(BOARD))
    b = pcbnew.LoadBoard(str(BOARD))
    obs = Obstacles(b)
    res = route(obs, (80.3, 122.0, 1), (80.65, 120.2, 1), nc, 0.10)
    print('B link:', bool(res))
    if res:
        add_route(b, netobj, 0.10, res[0], res[1])
        b.Save(str(BOARD))
