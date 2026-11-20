import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, add_route, route

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
BOARD = TREE / 'wmatrix.kicad_pcb'
b = pcbnew.LoadBoard(str(BOARD))
obs = Obstacles(b)
netobj = b.FindNet('HALL_3V3')
res = route(obs, (105.0, 120.156067, 0), (97.067925, 120.375, 0), netobj.GetNetCode(), 0.10)
assert res, 'neck route failed'
add_route(b, netobj, 0.10, res[0], res[1])
b.Save(str(BOARD))
print('rail neck placed (0.10mm, C_MUX_B pad1 -> U_MUXB pin2)')
