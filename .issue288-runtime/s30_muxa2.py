import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, add_route, route, _seg_clear

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
BOARD = TREE / 'wmatrix.kicad_pcb'
b = pcbnew.LoadBoard(str(BOARD))
netobj = b.FindNet('MUXA_OUT')
nc = netobj.GetNetCode()
obs = Obstacles(b)
ok = _seg_clear(obs, 79.067925, 124.275, 82.0, 124.275, 0, nc, 0.05)
print('channel segment clear:', ok)
viaok = not (obs.blocked(82.0, 124.275, 0, nc, 0.30, via=True) or obs.blocked(82.0, 124.275, 1, nc, 0.30, via=True))
print('via legal at (82,124.275):', viaok)
if ok and viaok:
    add_route(b, netobj, 0.10, [(79.067925, 124.275, 0), (82.0, 124.275, 0)], [(82.0, 124.275)])
    b.Save(str(BOARD))
    b = pcbnew.LoadBoard(str(BOARD))
    obs = Obstacles(b)
    res = route(obs, (82.0, 124.275, 1), (82.0, 127.0, 0), nc, 0.10)
    print('B run to TP web:', bool(res))
    if res:
        add_route(b, netobj, 0.10, res[0], res[1])
        b.Save(str(BOARD))
