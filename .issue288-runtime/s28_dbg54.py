import math, sys
from pathlib import Path
import pcbnew
MM = 1e6
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
for t in list(b.GetTracks()):
    if t.GetNetname() != 'HALL_3V3':
        continue
    if t.Type() == pcbnew.PCB_VIA_T:
        p = t.GetPosition()
        if 112 < p.x / MM < 126 and 96 < p.y / MM < 124:
            print('VIA', (round(p.x / MM, 2), round(p.y / MM, 2)))
    else:
        s, e = t.GetStart(), t.GetEnd()
        if (112 < s.x / MM < 126 and 96 < s.y / MM < 124) or (112 < e.x / MM < 126 and 96 < e.y / MM < 124):
            lay = 'F' if t.GetLayer() == pcbnew.F_Cu else 'B'
            print(lay, (round(s.x / MM, 2), round(s.y / MM, 2)), (round(e.x / MM, 2), round(e.y / MM, 2)), 'w', round(t.GetWidth() / MM, 2))
