import math, sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, add_route, _seg_clear
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
        if t.Type() != pcbnew.PCB_TRACE_T or t.GetNetname() != 'H_B3_RAW':
            continue
        s, e = t.GetStart(), t.GetEnd()
        if math.hypot(s.x / MM - 97.562357, s.y / MM - 113.344432) < 0.35 or \
           math.hypot(e.x / MM - 97.562357, e.y / MM - 113.344432) < 0.35:
            b.Remove(t); n += 1
    b.Save(str(BOARD))
    print('deleted', n)
elif step == 'ha0':
    netobj = b.FindNet('H_A0_RAW')
    nc = netobj.GetNetCode()
    obs = Obstacles(b)
    for pts in [[(79.9, 121.7, 0), (80.3, 121.35, 0), (80.45, 120.75, 0)],
                [(79.9, 121.7, 0), (80.15, 121.5, 0), (80.45, 120.75, 0)],
                [(79.9, 121.7, 0), (80.45, 121.2, 0), (80.45, 120.75, 0)]]:
        ok = all(_seg_clear(obs, a[0], a[1], c[0], c[1], 0, nc, 0.05) for a, c in zip(pts, pts[1:]))
        print('candidate clear:', ok)
        if ok:
            add_route(b, netobj, 0.10, pts, [])
            b.Save(str(BOARD))
            print('placed')
            break
elif step == 'hb3':
    for attempt in range(3):
        obs = Obstacles(b)
        comp = Comp(b)
        comps = comp.components('H_B3_RAW')
        if len(comps) <= 1:
            break
        if not try_connect(b, obs, comp, 'H_B3_RAW', comps):
            print('FAILED', [len(c) for c in comps])
            break
        b.Save(str(BOARD))
        b = pcbnew.LoadBoard(str(BOARD))
    comp = Comp(b)
    print('H_B3_RAW comps:', [len(c) for c in comp.components('H_B3_RAW')])
