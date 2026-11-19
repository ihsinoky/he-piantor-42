import math, sys
from pathlib import Path
import pcbnew
MM = 1e6
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
tx, ty = 49.75, 73.3
for t in list(b.GetTracks()):
    if t.Type() == pcbnew.PCB_VIA_T:
        continue
    s, e = t.GetStart(), t.GetEnd()
    ax, ay, bx, by = s.x / MM, s.y / MM, e.x / MM, e.y / MM
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    tt = 0.0 if L2 == 0 else max(0.0, min(1.0, ((tx - ax) * dx + (ty - ay) * dy) / L2))
    d = math.hypot(tx - (ax + tt * dx), ty - (ay + tt * dy))
    if d < 1.0:
        lay = 'F' if t.GetLayer() == pcbnew.F_Cu else 'B'
        print('SEG', t.GetNetname(), lay, (round(ax, 2), round(ay, 2)), (round(bx, 2), round(by, 2)), 'dist', round(d, 3), 'w', round(t.GetWidth() / MM, 2))
