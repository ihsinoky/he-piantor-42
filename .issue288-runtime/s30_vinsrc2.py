import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, add_route, route, _seg_clear

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
BOARD = TREE / 'wmatrix.kicad_pcb'
b = pcbnew.LoadBoard(str(BOARD))
netobj = b.FindNet('VIN_SRC')
nc = netobj.GetNetCode()
obs = Obstacles(b)
hop1 = [(148.6, 134.2, 0), (147.95, 134.2, 0), (147.95, 132.9, 0), (147.55, 132.35, 0)]
hop2 = [(152.30, 132.71, 0), (152.30, 134.2, 0), (148.6, 134.2, 0)]
for name, pts in (('hop1 via->pad11', hop1), ('hop2 pad2stub->via', hop2)):
    ok = all(_seg_clear(obs, a[0], a[1], c[0], c[1], 0, nc, 0.15) for a, c in zip(pts, pts[1:]))
    print(name, 'clear:', ok)
    if ok:
        add_route(b, netobj, 0.30, pts, [])
        obs = Obstacles(b)
b.Save(str(BOARD))
b = pcbnew.LoadBoard(str(BOARD))
obs = Obstacles(b)
res = route(obs, (148.6, 134.2, 1), (142.548019, 128.798019, 1), nc, 0.30)
print('B run via->B track:', bool(res))
if res:
    add_route(b, netobj, 0.30, res[0], res[1])
    b.Save(str(BOARD))
