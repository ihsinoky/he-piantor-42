"""S2.4l: final four fixes."""
import math
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, add_route, route, _seg_clear

WT = Path('/home/hatch/workspace/projects/he-piantor-wmatrix')
TREE = WT / 'hardware/kicad/qualification/issue-288-wmatrix'
BOARD = TREE / 'wmatrix.kicad_pcb'
MM = 1e6
step = sys.argv[1]
b = pcbnew.LoadBoard(str(BOARD))

if step == 'del':
    n = 0
    for t in list(b.GetTracks()):
        if t.Type() != pcbnew.PCB_TRACE_T:
            continue
        s = t.GetStart()
        if t.GetNetname() == 'H_A5_RAW' and math.hypot(s.x / MM - 117.577586, s.y / MM - 106.727586) < 0.3:
            b.Remove(t); n += 1
        if t.GetNetname() == 'EN_C' and math.hypot(s.x / MM - 151.0, s.y / MM - 91.2) < 0.3:
            b.Remove(t); n += 1
        if t.GetNetname() == 'EN_C' and math.hypot(s.x / MM - 151.25, s.y / MM - 90.7) < 0.3:
            b.Remove(t); n += 1
    b.Save(str(BOARD))
    print('deleted', n)

elif step == 'ha5':
    netobj = b.FindNet('H_A5_RAW')
    nc = netobj.GetNetCode()
    obs = Obstacles(b)
    pts = [(117.25, 106.3, 0), (118.75, 106.3, 0), (118.75, 109.5, 0)]
    ok = all(_seg_clear(obs, a[0], a[1], c[0], c[1], 0, nc, 0.05) for a, c in zip(pts, pts[1:]))
    print('HA5 arc clear:', ok)
    if ok:
        add_route(b, netobj, 0.10, pts, [])
        b.Save(str(BOARD))
        b = pcbnew.LoadBoard(str(BOARD))
        obs = Obstacles(b)
        res = route(obs, (118.75, 109.5, 0), (109.9, 113.7, 0), nc, 0.10)
        print('HA5 arc->trunk:', bool(res))
        if res:
            add_route(b, netobj, 0.10, res[0], res[1])
            b.Save(str(BOARD))

elif step == 'hc4en':
    netobj = b.FindNet('EN_C')
    nc = netobj.GetNetCode()
    obs = Obstacles(b)
    ok = _seg_clear(obs, 151.25, 90.7, 150.9, 90.9, 0, nc, 0.05)
    vok = not (obs.blocked(150.9, 90.9, 0, nc, 0.30, via=True) or obs.blocked(150.9, 90.9, 1, nc, 0.30, via=True))
    print('HC4 EN F hop clear:', ok, 'via legal:', vok)
    if ok and vok:
        add_route(b, netobj, 0.10, [(151.25, 90.7, 0), (150.9, 90.9, 0)], [(150.9, 90.9)])
        b.Save(str(BOARD))
        b = pcbnew.LoadBoard(str(BOARD))
        obs = Obstacles(b)
        res = route(obs, (150.9, 90.9, 1), (150.25, 91.20, 1), nc, 0.10)
        print('HC4 EN B hop:', bool(res))
        if res:
            add_route(b, netobj, 0.10, res[0], res[1])
            b.Save(str(BOARD))

elif step == 'bridges':
    for net, pa, pb, w in [('HALL_3V3', (150.75, 72.16, 0), (150.75, 89.156067, 0), 0.30),
                           ('H_C5_RAW', (150.00, 112.05, 1), (149.45, 108.55, 1), 0.10)]:
        b = pcbnew.LoadBoard(str(BOARD))
        netobj = b.FindNet(net)
        obs = Obstacles(b)
        res = route(obs, pa, pb, netobj.GetNetCode(), w)
        print(net, 'bridge:', bool(res))
        if res:
            add_route(b, netobj, w, res[0], res[1])
            b.Save(str(BOARD))
