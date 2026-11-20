"""S2.4j: HB3 OUT east-arc hand path; HA5 EN graze fix."""
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

if step == 'hb3':
    netobj = b.FindNet('H_B3_RAW')
    nc = netobj.GetNetCode()
    obs = Obstacles(b)
    pts = [(134.25, 72.3, 0), (135.0, 71.9, 0), (136.5, 72.5, 0),
           (136.5, 74.3, 0), (134.25, 74.3, 0)]
    ok = all(_seg_clear(obs, a[0], a[1], c[0], c[1], 0, nc, 0.05) for a, c in zip(pts, pts[1:]))
    print('HB3 east arc clear:', ok)
    if ok:
        add_route(b, netobj, 0.10, pts, [])
        b.Save(str(BOARD))

elif step == 'ha5del':
    n = 0
    for t in list(b.GetTracks()):
        if t.Type() != pcbnew.PCB_TRACE_T or t.GetNetname() != 'EN_A':
            continue
        if t.GetLayer() != pcbnew.F_Cu:
            continue
        s, e = t.GetStart(), t.GetEnd()
        if math.hypot(s.x / MM - 117.25, s.y / MM - 107.7) < 1.6 or \
           math.hypot(e.x / MM - 117.25, e.y / MM - 107.7) < 1.6:
            b.Remove(t)
            n += 1
    b.Save(str(BOARD))
    print('deleted', n, 'EN_A F segs near HA5 pad')

elif step == 'ha5':
    netobj = b.FindNet('EN_A')
    nc = netobj.GetNetCode()
    obs = Obstacles(b)
    ok = _seg_clear(obs, 117.25, 107.7, 117.75, 108.2, 0, nc, 0.05)
    print('HA5 SE stub clear:', ok)
    if ok:
        add_route(b, netobj, 0.10, [(117.25, 107.7, 0), (117.75, 108.2, 0)], [])
        b.Save(str(BOARD))
        b = pcbnew.LoadBoard(str(BOARD))
        obs = Obstacles(b)
        res = route(obs, (117.75, 108.2, 0), (115.869643, 104.319643, 0), nc, 0.10)
        print('HA5 stub->via:', bool(res))
        if res:
            add_route(b, netobj, 0.10, res[0], res[1])
            b.Save(str(BOARD))
