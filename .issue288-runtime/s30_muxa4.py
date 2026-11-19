import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, add_route, _seg_clear

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
BOARD = TREE / 'wmatrix.kicad_pcb'
b = pcbnew.LoadBoard(str(BOARD))
netobj = b.FindNet('MUXA_OUT')
nc = netobj.GetNetCode()
obs = Obstacles(b)
ok = _seg_clear(obs, 78.16, 123.95, 78.21, 123.77, 0, nc, 0.05)
print('micro-hop clear:', ok)
if ok:
    add_route(b, netobj, 0.10, [(78.16, 123.95, 0), (78.21, 123.77, 0)], [])
    b.Save(str(BOARD))
