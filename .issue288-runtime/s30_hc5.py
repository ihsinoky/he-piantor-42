import math, sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, add_route, route
from s28_component_route import Comp
from s29_finish import escape_pad, try_connect

WT = Path('/home/hatch/workspace/projects/he-piantor-wmatrix')
TREE = WT / 'hardware/kicad/qualification/issue-288-wmatrix'
BOARD = TREE / 'wmatrix.kicad_pcb'
MM = 1e6
step = sys.argv[1]
b = pcbnew.LoadBoard(str(BOARD))
if step == 'del':
    n = 0
    for t in list(b.GetTracks()):
        if t.Type() != pcbnew.PCB_TRACE_T or t.GetNetname() != 'GND':
            continue
        s, e = t.GetStart(), t.GetEnd()
        seg = (round(s.x / MM, 2), round(s.y / MM, 2), round(e.x / MM, 2), round(e.y / MM, 2))
        if seg in [(151.00, 108.20, 154.25, 107.95), (154.25, 107.95, 151.00, 108.20)]:
            b.Remove(t); n += 1
    b.Save(str(BOARD))
    print('deleted', n)
elif step == 'en':
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
elif step == 'gnd':
    comp = Comp(b)
    obs = Obstacles(b)
    comps = comp.components('GND')
    print('GND comps:', [len(c) for c in comps])
    if len(comps) > 1 and try_connect(b, obs, comp, 'GND', comps):
        b.Save(str(BOARD))
        print('GND reconnected')
elif step == 'raw':
    netobj = b.FindNet('H_C5_RAW')
    obs = Obstacles(b)
    res = route(obs, (151.25, 106.3, 0), (150.0, 112.0, 0), netobj.GetNetCode(), 0.10)
    print('HC5 RAW hop:', bool(res))
    if res:
        add_route(b, netobj, 0.10, res[0], res[1])
        b.Save(str(BOARD))
