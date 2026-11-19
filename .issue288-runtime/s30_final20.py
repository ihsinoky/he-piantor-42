import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, add_route, _seg_clear

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
BOARD = TREE / 'wmatrix.kicad_pcb'
b = pcbnew.LoadBoard(str(BOARD))
netobj = b.FindNet('H_B3_RAW')
nc = netobj.GetNetCode()
obs = Obstacles(b)
pts = [(97.562, 113.094, 0), (97.585, 113.20, 0), (97.585, 113.48, 0), (97.560, 113.590, 0)]
ok = all(_seg_clear(obs, a[0], a[1], c[0], c[1], 0, nc, 0.05) for a, c in zip(pts, pts[1:]))
print('jog clear:', ok)
if ok:
    add_route(b, netobj, 0.10, pts, [])
    b.Save(str(BOARD))
    print('placed')
