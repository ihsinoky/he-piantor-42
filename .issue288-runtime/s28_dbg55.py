import math, sys
from pathlib import Path
import pcbnew
MM = 1e6
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
for (tx, ty) in [(120.7, 107.0), (116.4, 103.7)]:
    print('near', (tx, ty))
    for t in list(b.GetTracks()):
        if t.GetNetname() != 'HALL_3V3':
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            continue
        s, e = t.GetStart(), t.GetEnd()
        for p in (s, e):
            if math.hypot(p.x / MM - tx, p.y / MM - ty) < 0.4:
                lay = 'F' if t.GetLayer() == pcbnew.F_Cu else 'B'
                print(' ', lay, (round(s.x / MM, 2), round(s.y / MM, 2)), (round(e.x / MM, 2), round(e.y / MM, 2)))
                break
