import math, sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, add_route, route
from s28_component_route import Comp

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
BOARD = TREE / 'wmatrix.kicad_pcb'
MM = 1e6
step = sys.argv[1]
b = pcbnew.LoadBoard(str(BOARD))
if step == 'del':
    n = 0
    targets = [((79.07, 121.03), (80.50, 121.15)), ((80.50, 121.15), (81.00, 120.65))]
    for t in list(b.GetTracks()):
        if t.Type() != pcbnew.PCB_TRACE_T or t.GetNetname() != 'GND':
            continue
        s, e = t.GetStart(), t.GetEnd()
        sp = (round(s.x / MM, 2), round(s.y / MM, 2))
        ep = (round(e.x / MM, 2), round(e.y / MM, 2))
        if (sp, ep) in targets or (ep, sp) in targets:
            b.Remove(t); n += 1
    b.Save(str(BOARD))
    print('deleted', n)
elif step == 'ha0':
    netobj = b.FindNet('H_A0_RAW')
    obs = Obstacles(b)
    res = route(obs, (79.9, 121.7, 0), (80.45, 120.75, 0), netobj.GetNetCode(), 0.10)
    print('HA0 route:', bool(res))
    if res:
        add_route(b, netobj, 0.10, res[0], res[1])
        b.Save(str(BOARD))
elif step == 'check':
    comp = Comp(b)
    for net in ['H_A0_RAW', 'GND']:
        print(net, 'comps:', [len(c) for c in comp.components(net)])
