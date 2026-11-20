import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, add_route, route
from s28_component_route import Comp
from s29_finish import try_connect

WT = Path('/home/hatch/workspace/projects/he-piantor-wmatrix')
TREE = WT / 'hardware/kicad/qualification/issue-288-wmatrix'
BOARD = TREE / 'wmatrix.kicad_pcb'
MM = 1e6
step = sys.argv[1]
b = pcbnew.LoadBoard(str(BOARD))
cx, cy = 117.0, 107.0
if step == 'del':
    n = 0
    for t in list(b.GetTracks()):
        if t.Type() != pcbnew.PCB_TRACE_T or t.GetNetname() != 'H_A5_RAW':
            continue
        s, e = t.GetStart(), t.GetEnd()
        if all(abs(q.x / MM - cx) <= 3.2 and abs(q.y / MM - cy) <= 3.2 for q in (s, e)):
            b.Remove(t); n += 1
    b.Save(str(BOARD))
    print('deleted', n, 'H_A5_RAW cage segs')
elif step == 'route':
    netobj = b.FindNet('EN_A')
    obs = Obstacles(b)
    res = route(obs, (117.25, 107.7, 0), (115.869643, 104.319643, 0), netobj.GetNetCode(), 0.10)
    print('EN_A HA5 pad->via:', bool(res))
    if res:
        add_route(b, netobj, 0.10, res[0], res[1])
        b.Save(str(BOARD))
        b = pcbnew.LoadBoard(str(BOARD))
        obs = Obstacles(b)
        comp = Comp(b)
        comps = comp.components('H_A5_RAW')
        print('H_A5_RAW comps:', len(comps))
        if len(comps) > 1 and try_connect(b, obs, comp, 'H_A5_RAW', comps):
            b.Save(str(BOARD))
            print('H_A5_RAW reconnected')
