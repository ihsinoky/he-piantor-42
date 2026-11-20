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
        if t.GetNetname() != 'MUXA_OUT':
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            if math.hypot(p.x / MM - 80.45, p.y / MM - 124.05) < 0.3:
                b.Remove(t); n += 1
        else:
            s, e = t.GetStart(), t.GetEnd()
            seg = (round(s.x / MM, 2), round(s.y / MM, 2), round(e.x / MM, 2), round(e.y / MM, 2))
            if seg in [(78.45, 124.05, 80.45, 124.05), (80.45, 124.05, 78.45, 124.05),
                       (78.60, 124.10, 78.60, 124.04), (78.60, 124.04, 78.60, 124.10),
                       (80.45, 124.05, 80.20, 125.30), (80.20, 125.30, 80.45, 124.05)]:
                b.Remove(t); n += 1
    b.Save(str(BOARD))
    print('deleted', n)
elif step == 'place':
    netobj = b.FindNet('MUXA_OUT')
    nc = netobj.GetNetCode()
    obs = Obstacles(b)
    ok = _seg_clear(obs, 78.45, 124.20, 80.45, 124.20, 0, nc, 0.05)
    vok = not (obs.blocked(80.45, 124.20, 0, nc, 0.30, via=True) or obs.blocked(80.45, 124.20, 1, nc, 0.30, via=True))
    bok = _seg_clear(obs, 80.45, 124.20, 80.20, 125.30, 1, nc, 0.05)
    print('track clear:', ok, 'via legal:', vok, 'B seg clear:', bok)
    if ok and vok and bok:
        add_route(b, netobj, 0.10, [(78.45, 124.20, 0), (80.45, 124.20, 0)], [(80.45, 124.20)])
        add_route(b, netobj, 0.10, [(80.45, 124.20, 1), (80.20, 125.30, 1)], [])
        b.Save(str(BOARD))
        print('placed')
