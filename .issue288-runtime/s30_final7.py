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
if step == 'del':
    n = 0
    for t in list(b.GetTracks()):
        if t.Type() != pcbnew.PCB_TRACE_T or t.GetNetname() != 'H_A5_RAW':
            continue
        s, e = t.GetStart(), t.GetEnd()
        L = math.hypot(e.x - s.x, e.y - s.y) / MM
        near = math.hypot(s.x / MM - 117.327586, s.y / MM - 106.477586) < 0.3 or \
               math.hypot(s.x / MM - 117.577586, s.y / MM - 106.727586) < 0.3
        if near and L > 0.3:
            b.Remove(t); n += 1
    b.Save(str(BOARD))
    print('deleted', n)
elif step == 'ha5':
    netobj = b.FindNet('H_A5_RAW')
    nc = netobj.GetNetCode()
    obs = Obstacles(b)
    ok = _seg_clear(obs, 117.327586, 106.477586, 118.3, 106.1, 0, nc, 0.05)
    print('HA5 NE hop clear:', ok)
    if ok:
        add_route(b, netobj, 0.10, [(117.327586, 106.477586, 0), (118.3, 106.55, 0)], [])
        b.Save(str(BOARD))
        b = pcbnew.LoadBoard(str(BOARD))
        obs = Obstacles(b)
        res = route(obs, (118.3, 106.55, 0), (118.577586, 108.477586, 0), nc, 0.10)
        print('HA5 hop->track:', bool(res))
        if res:
            add_route(b, netobj, 0.10, res[0], res[1])
            b.Save(str(BOARD))
elif step == 'enc':
    obs = Obstacles(b)
    comp = Comp(b)
    comps = comp.components('EN_C')
    print('EN_C comps:', [len(c) for c in comps])
    if len(comps) > 1 and try_connect(b, obs, comp, 'EN_C', comps):
        b.Save(str(BOARD))
        print('EN_C connected')
