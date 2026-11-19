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
src, dst = (97.067925, 120.375, 0), (121.0, 130.95, 0)
res = route(obs, src, dst, netobj.GetNetCode(), 0.30)
w = 0.30
if not res:
    res = route(obs, src, dst, netobj.GetNetCode(), 0.10)
    w = 0.10
assert res, 'rail link 2 failed at both widths'
add_route(b, netobj, w, res[0], res[1])
b.Save(str(BOARD))
print(f'rail link 2 placed at width {w} (U_MUXB pin2 -> R_SHUNT rail pad)')
