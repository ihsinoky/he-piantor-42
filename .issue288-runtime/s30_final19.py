import math, sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, add_route, _seg_clear

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
        s = t.GetStart()
        if math.hypot(s.x / MM - 97.562357, s.y / MM - 113.344432) < 0.3 and t.GetLength() / MM < 0.35:
            b.Remove(t); n += 1
    b.Save(str(BOARD))
    print('deleted', n)
elif step == 'place':
    netobj = b.FindNet('H_B3_RAW')
    nc = netobj.GetNetCode()
    obs = Obstacles(b)
    pts = [(97.562357, 113.344432, 0), (97.85, 113.47, 0), (97.56, 113.59, 0)]
    ok = all(_seg_clear(obs, a[0], a[1], c[0], c[1], 0, nc, 0.05) for a, c in zip(pts, pts[1:]))
    print('detour clear:', ok)
    if ok:
        add_route(b, netobj, 0.10, pts, [])
        b.Save(str(BOARD))
        print('placed')
