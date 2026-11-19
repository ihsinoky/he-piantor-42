import math, sys
from pathlib import Path
import pcbnew
MM = 1e6
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
for (tx, ty) in [(116.75, 89.3), (84.9, 121.7)]:
    print('near', (tx, ty))
    for t in list(b.GetTracks()):
        if t.GetNetname() != 'HALL_3V3':
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            if math.hypot(p.x / MM - tx, p.y / MM - ty) < 1.6:
                print('  VIA', (round(p.x / MM, 2), round(p.y / MM, 2)))
        else:
            s, e = t.GetStart(), t.GetEnd()
            ax, ay, bx, by = s.x / MM, s.y / MM, e.x / MM, e.y / MM
            dx, dy = bx - ax, by - ay
            L2 = dx * dx + dy * dy
            tt = 0.0 if L2 == 0 else max(0.0, min(1.0, ((tx - ax) * dx + (ty - ay) * dy) / L2))
            d = math.hypot(tx - (ax + tt * dx), ty - (ay + tt * dy))
            if d < 1.2:
                lay = 'F' if t.GetLayer() == pcbnew.F_Cu else 'B'
                print('  SEG', lay, (round(ax, 2), round(ay, 2)), (round(bx, 2), round(by, 2)), 'dist', round(d, 3))
