"""S2.4i MUXA_OUT local rebuild: delete all MUXA_OUT tracks/vias in the
box (76..90, 122..130), then route pin8 -> TP -> west web cleanly.
"""
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, add_route, route

WT = Path('/home/hatch/workspace/projects/he-piantor-wmatrix')
TREE = WT / 'hardware/kicad/qualification/issue-288-wmatrix'
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
            pts = [(p.x / MM, p.y / MM)]
        else:
            s, e = t.GetStart(), t.GetEnd()
            pts = [(s.x / MM, s.y / MM), (e.x / MM, e.y / MM)]
        if all(76 <= x <= 90 and 122 <= y <= 130 for x, y in pts):
            b.Remove(t)
            n += 1
    b.Save(str(BOARD))
    print('deleted', n, 'MUXA_OUT items in box')

elif step == 'route':
    netobj = b.FindNet('MUXA_OUT')
    nc = netobj.GetNetCode()
    obs = Obstacles(b)
    res = route(obs, (79.067925, 124.275, 0), (82.0, 127.0, 0), nc, 0.10)
    print('pin8 -> TP:', bool(res))
    if res:
        add_route(b, netobj, 0.10, res[0], res[1])
        b.Save(str(BOARD))
        b = pcbnew.LoadBoard(str(BOARD))
        obs = Obstacles(b)
    res = route(obs, (82.0, 127.0, 0), (74.17, 123.92, 1), nc, 0.10)
    print('TP -> west web B:', bool(res))
    if res:
        add_route(b, netobj, 0.10, res[0], res[1])
        b.Save(str(BOARD))
