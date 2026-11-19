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
f_ok = _seg_clear(obs, 78.17, 123.92, 77.75, 123.15, 0, nc, 0.05)
b_ok = _seg_clear(obs, 77.75, 123.15, 77.95, 123.55, 1, nc, 0.05)
v_ok = not (obs.blocked(77.75, 123.15, 0, nc, 0.30, via=True) or obs.blocked(77.75, 123.15, 1, nc, 0.30, via=True))
print('F seg:', f_ok, 'B seg:', b_ok, 'via:', v_ok)
if f_ok and b_ok and v_ok:
    add_route(b, netobj, 0.10, [(78.17, 123.92, 0), (77.75, 123.15, 0)], [(77.75, 123.15)])
    add_route(b, netobj, 0.10, [(77.75, 123.15, 1), (77.95, 123.55, 1)], [])
    b.Save(str(BOARD))
    print('placed')
