import math, sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, route, add_route
from s28_component_route import Comp
from s29_finish import try_connect

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
BOARD = TREE / 'wmatrix.kicad_pcb'
MM = 1e6
step = sys.argv[1]
b = pcbnew.LoadBoard(str(BOARD))
if step == 'del':
    n = 0
    for t in list(b.GetTracks()):
        if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() == 'MUX_A0':
            p = t.GetPosition()
            if math.hypot(p.x / MM - 80.5, p.y / MM - 118.9) < 0.3:
                b.Remove(t); n += 1
        elif t.Type() == pcbnew.PCB_TRACE_T and t.GetNetname() == 'MUX_A0':
            s, e = t.GetStart(), t.GetEnd()
            if math.hypot(s.x / MM - 80.5, s.y / MM - 118.9) < 1.3 or math.hypot(e.x / MM - 80.5, e.y / MM - 118.9) < 1.3:
                b.Remove(t); n += 1
        elif t.Type() == pcbnew.PCB_TRACE_T and t.GetNetname() == 'H_B3_RAW':
            s = t.GetStart()
            if math.hypot(s.x / MM - 97.562357, s.y / MM - 113.344432) < 0.3:
                b.Remove(t); n += 1
    b.Save(str(BOARD))
    print('deleted', n)
elif step == 'fix':
    for net, pa, pb in [('H_A0_RAW', (80.45, 120.75, 0), (79.9, 121.7, 0))]:
        netobj = b.FindNet(net)
        obs = Obstacles(b)
        res = route(obs, pa, pb, netobj.GetNetCode(), 0.10)
        print(net, 'stub bridge:', bool(res))
        if res:
            add_route(b, netobj, 0.10, res[0], res[1])
            b.Save(str(BOARD))
            b = pcbnew.LoadBoard(str(BOARD))
    for net in ['MUX_A0', 'H_B3_RAW']:
        for attempt in range(3):
            obs = Obstacles(b)
            comp = Comp(b)
            comps = comp.components(net)
            if len(comps) <= 1:
                break
            if not try_connect(b, obs, comp, net, comps):
                print(net, 'reconnect FAILED', [len(c) for c in comps])
                break
        comp = Comp(b)
        print(net, 'comps:', [len(c) for c in comp.components(net)])
    b.Save(str(BOARD))
