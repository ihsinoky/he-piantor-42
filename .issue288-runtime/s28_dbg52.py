import math, sys
from pathlib import Path
import pcbnew
MM = 1e6
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
for (tx, ty) in [(109.05, 134.5), (103.3, 129.25)]:
    print('near', (tx, ty))
    for t in list(b.GetTracks()):
        if t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            if math.hypot(p.x / MM - tx, p.y / MM - ty) < 0.8:
                print('  VIA', t.GetNetname(), (round(p.x / MM, 3), round(p.y / MM, 3)))
        else:
            s, e = t.GetStart(), t.GetEnd()
            for p in (s, e):
                if math.hypot(p.x / MM - tx, p.y / MM - ty) < 0.8:
                    lay = 'F' if t.GetLayer() == pcbnew.F_Cu else 'B'
                    print('  SEG', t.GetNetname(), lay, (round(s.x / MM, 3), round(s.y / MM, 3)), (round(e.x / MM, 3), round(e.y / MM, 3)))
                    break
