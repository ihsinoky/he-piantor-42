import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, add_route, _seg_clear

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
BOARD = TREE / 'wmatrix.kicad_pcb'
b = pcbnew.LoadBoard(str(BOARD))
netobj = b.FindNet('H_A5_RAW')
nc = netobj.GetNetCode()
obs = Obstacles(b)
pts = [(117.328, 106.478, 0), (117.85, 106.45, 0), (117.85, 106.728, 0), (117.578, 106.728, 0)]
ok = all(_seg_clear(obs, a[0], a[1], c[0], c[1], 0, nc, 0.05) for a, c in zip(pts, pts[1:]))
print('HA5 corner bridge clear:', ok)
if ok:
    add_route(b, netobj, 0.10, pts, [])
    b.Save(str(BOARD))
    print('placed')
