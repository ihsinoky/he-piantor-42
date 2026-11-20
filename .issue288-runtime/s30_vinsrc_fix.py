import math, sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, add_route, route, _seg_clear

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
BOARD = TREE / 'wmatrix.kicad_pcb'
MM = 1e6
step = sys.argv[1]
b = pcbnew.LoadBoard(str(BOARD))
if step == 'del':
    n = 0
    for t in list(b.GetTracks()):
        if t.GetNetname() != 'VIN_SRC':
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            if math.hypot(p.x / MM - 147.700333, p.y / MM - 132.950333) < 0.4:
                b.Remove(t); n += 1
        elif t.Type() == pcbnew.PCB_TRACE_T:
            s = t.GetStart()
            if math.hypot(s.x / MM - 152.3, s.y / MM - 132.705) < 0.4:
                b.Remove(t); n += 1
    b.Save(str(BOARD))
    print('deleted', n, 'bad VIN_SRC items')
elif step == 'place':
    netobj = b.FindNet('VIN_SRC')
    nc = netobj.GetNetCode()
    obs = Obstacles(b)
    pts = [(148.6, 134.2, 0), (147.95, 134.2, 0), (147.95, 132.9, 0), (147.55, 132.35, 0)]
    ok = all(_seg_clear(obs, a[0], a[1], c[0], c[1], 0, nc, 0.15) for a, c in zip(pts, pts[1:]))
    print('F hop clear (0.30w):', ok)
    viaok = not (obs.blocked(148.6, 134.2, 0, nc, 0.30, via=True) or obs.blocked(148.6, 134.2, 1, nc, 0.30, via=True))
    print('via legal at (148.6,134.2):', viaok)
    if ok and viaok:
        add_route(b, netobj, 0.30, pts, [(148.6, 134.2)])
        b.Save(str(BOARD))
        b = pcbnew.LoadBoard(str(BOARD))
        obs = Obstacles(b)
        res = route(obs, (148.6, 134.2, 1), (142.548019, 128.798019, 1), nc, 0.30)
        print('B run to B-track end:', bool(res))
        if res:
            add_route(b, netobj, 0.30, res[0], res[1])
            b.Save(str(BOARD))
