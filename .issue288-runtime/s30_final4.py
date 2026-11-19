import math, sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, add_route, route, _seg_clear
from s28_component_route import Comp
from s29_finish import escape_pad, try_connect

WT = Path('/home/hatch/workspace/projects/he-piantor-wmatrix')
TREE = WT / 'hardware/kicad/qualification/issue-288-wmatrix'
BOARD = TREE / 'wmatrix.kicad_pcb'
MM = 1e6
step = sys.argv[1]
b = pcbnew.LoadBoard(str(BOARD))

if step == 'ha5del':
    n = 0
    for t in list(b.GetTracks()):
        if t.Type() != pcbnew.PCB_TRACE_T or t.GetNetname() != 'H_A5_RAW':
            continue
        s = t.GetStart()
        if math.hypot(s.x / MM - 117.577586, s.y / MM - 106.727586) < 0.3:
            b.Remove(t); n += 1
    b.Save(str(BOARD))
    print('deleted', n)
elif step == 'ha5fix':
    comp = Comp(b)
    obs = Obstacles(b)
    comps = comp.components('H_A5_RAW')
    print('comps:', [len(c) for c in comps])
    if len(comps) > 1 and try_connect(b, obs, comp, 'H_A5_RAW', comps):
        b.Save(str(BOARD))
        print('reconnected')
elif step == 'hc3':
    netobj = b.FindNet('HALL_3V3')
    nc = netobj.GetNetCode()
    obs = Obstacles(b)
    ok = _seg_clear(obs, 150.75, 72.32, 150.75, 72.14, 0, nc, 0.15)
    print('HC3 hop clear:', ok)
    if ok:
        add_route(b, netobj, 0.30, [(150.75, 72.32, 0), (150.75, 72.14, 0)], [])
        b.Save(str(BOARD))
elif step == 'hc5en':
    comp = Comp(b)
    obs = Obstacles(b)
    for c in comp.components('EN_C'):
        if len(c) == 1 and comp.items[c[0]]['kind'] == 'pad':
            it = comp.items[c[0]]
            if abs(it['x'] - 151.25) < 0.3 and abs(it['y'] - 107.7) < 0.3:
                ok = escape_pad(b, obs, 'EN_C', it)
                print('HC5 EN escape:', ok)
                if ok:
                    b.Save(str(BOARD))
                    b = pcbnew.LoadBoard(str(BOARD))
                    obs = Obstacles(b)
                    comp = Comp(b)
                    comps = comp.components('EN_C')
                    if len(comps) > 1 and try_connect(b, obs, comp, 'EN_C', comps):
                        b.Save(str(BOARD))
                        print('EN_C connected')
elif step == 'hc5raw':
    netobj = b.FindNet('H_C5_RAW')
    obs = Obstacles(b)
    res = route(obs, (151.25, 106.3, 0), (150.0, 112.0, 0), netobj.GetNetCode(), 0.10)
    print('HC5 RAW hop:', bool(res))
    if res:
        add_route(b, netobj, 0.10, res[0], res[1])
        b.Save(str(BOARD))
