import math, sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, add_route, route, _seg_clear
from s28_component_route import Comp
from s29_finish import try_connect

WT = Path('/home/hatch/workspace/projects/he-piantor-wmatrix')
TREE = WT / 'hardware/kicad/qualification/issue-288-wmatrix'
BOARD = TREE / 'wmatrix.kicad_pcb'
MM = 1e6
step = sys.argv[1]
b = pcbnew.LoadBoard(str(BOARD))
if step == 'info':
    for t in list(b.GetTracks()):
        if t.Type() != pcbnew.PCB_TRACE_T or t.GetNetname() != 'H_A5_RAW':
            continue
        s, e = t.GetStart(), t.GetEnd()
        if math.hypot(s.x / MM - 118.577586, s.y / MM - 108.477586) < 0.3 or \
           math.hypot(s.x / MM - 117.327586, s.y / MM - 106.477586) < 0.3:
            print(f'({s.x/MM:.3f},{s.y/MM:.3f})->({e.x/MM:.3f},{e.y/MM:.3f})')
elif step == 'ha5':
    netobj = b.FindNet('H_A5_RAW')
    obs = Obstacles(b)
    res = route(obs, (117.327586, 106.477586, 0), (118.577586, 108.477586, 0), netobj.GetNetCode(), 0.10)
    print('HA5 bridge:', bool(res))
    if res:
        add_route(b, netobj, 0.10, res[0], res[1])
        b.Save(str(BOARD))
elif step == 'encdel':
    n = 0
    for t in list(b.GetTracks()):
        if t.Type() != pcbnew.PCB_TRACE_T or t.GetNetname() != 'H_C4_RAW':
            continue
        s, e = t.GetStart(), t.GetEnd()
        seg = (round(s.x / MM, 2), round(s.y / MM, 2), round(e.x / MM, 2), round(e.y / MM, 2))
        if seg in [(138.00, 106.80, 151.75, 90.80), (151.75, 90.80, 138.00, 106.80)]:
            b.Remove(t); n += 1
    b.Save(str(BOARD))
    print('deleted', n, 'trunk diagonal')
elif step == 'enc':
    netobj = b.FindNet('EN_C')
    nc = netobj.GetNetCode()
    obs = Obstacles(b)
    ok = _seg_clear(obs, 151.25, 90.7, 151.37, 91.57, 0, nc, 0.05)
    print('HC4 EN hop clear:', ok)
    if ok:
        add_route(b, netobj, 0.10, [(151.25, 90.7, 0), (151.37, 91.57, 0)], [])
        b.Save(str(BOARD))
elif step == 'c4raw':
    obs = Obstacles(b)
    comp = Comp(b)
    comps = comp.components('H_C4_RAW')
    print('H_C4_RAW comps:', [len(c) for c in comps])
    if len(comps) > 1 and try_connect(b, obs, comp, 'H_C4_RAW', comps):
        b.Save(str(BOARD))
        print('C4 RAW reconnected')
