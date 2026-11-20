import math, sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles
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
        if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() == 'EN_B':
            p = t.GetPosition()
            if math.hypot(p.x / MM - 97.12, p.y / MM - 113.45) < 0.3:
                b.Remove(t); n += 1
        elif t.Type() == pcbnew.PCB_TRACE_T and t.GetNetname() == 'EN_B':
            s, e = t.GetStart(), t.GetEnd()
            if math.hypot(s.x / MM - 97.12, s.y / MM - 113.45) < 1.1 or math.hypot(e.x / MM - 97.12, e.y / MM - 113.45) < 1.1:
                b.Remove(t); n += 1
        elif t.Type() == pcbnew.PCB_TRACE_T and t.GetNetname() == 'H_B3_RAW':
            s = t.GetStart()
            L = t.GetLength() / MM
            if math.hypot(s.x / MM - 97.562357, s.y / MM - 113.344432) < 0.3 and L < 0.35:
                b.Remove(t); n += 1
    b.Save(str(BOARD))
    print('deleted', n)
elif step == 'fix':
    for net in ['EN_B', 'H_B3_RAW']:
        for attempt in range(3):
            obs = Obstacles(b)
            comp = Comp(b)
            comps = comp.components(net)
            if len(comps) <= 1:
                break
            if not try_connect(b, obs, comp, net, comps):
                print(net, 'FAILED', [len(c) for c in comps])
                break
            b.Save(str(BOARD))
            b = pcbnew.LoadBoard(str(BOARD))
        comp = Comp(b)
        print(net, 'comps:', [len(c) for c in comp.components(net)])
