import math, sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, add_route, _seg_clear

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
BOARD = TREE / 'wmatrix.kicad_pcb'
MM = 1e6
step = sys.argv[1]
b = pcbnew.LoadBoard(str(BOARD))
if step == 'del':
    n = 0
    for t in list(b.GetTracks()):
        if t.Type() != pcbnew.PCB_TRACE_T:
            continue
        s, e = t.GetStart(), t.GetEnd()
        seg = (round(s.x / MM, 2), round(s.y / MM, 2), round(e.x / MM, 2), round(e.y / MM, 2))
        if t.GetNetname() == 'MUXA_OUT' and seg in [(77.95, 123.55, 78.20, 123.80), (78.20, 123.80, 77.95, 123.55)]:
            b.Remove(t); n += 1
        if t.GetNetname() == 'VIN_SRC' and seg in [(152.30, 132.71, 152.30, 134.20), (152.30, 134.20, 152.30, 132.71)]:
            b.Remove(t); n += 1
    b.Save(str(BOARD))
    print('deleted', n)
elif step == 'place':
    netobj = b.FindNet('VIN_SRC')
    nc = netobj.GetNetCode()
    obs = Obstacles(b)
    ok = _seg_clear(obs, 152.30, 132.71, 151.6, 134.2, 0, nc, 0.15)
    print('VIN_SRC diagonal clear:', ok)
    if ok:
        add_route(b, netobj, 0.30, [(152.30, 132.71, 0), (151.6, 134.2, 0)], [])
        b.Save(str(BOARD))
