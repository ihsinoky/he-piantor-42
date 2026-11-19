import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, add_route, route

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
BOARD = TREE / 'wmatrix.kicad_pcb'
b = pcbnew.LoadBoard(str(BOARD))
netobj = b.FindNet('MUXA_OUT')
obs = Obstacles(b)
res = route(obs, (80.20, 125.30, 1), (79.70, 126.30, 1), netobj.GetNetCode(), 0.10)
print('B bridge 2:', bool(res))
if res:
    add_route(b, netobj, 0.10, res[0], res[1])
    b.Save(str(BOARD))
