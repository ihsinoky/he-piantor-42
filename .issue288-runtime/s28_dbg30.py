import sys
from pathlib import Path
import pcbnew
MM = 1e6
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
for t in list(b.GetTracks()):
    if t.Type() != pcbnew.PCB_TRACE_T:
        continue
    s, e = t.GetStart(), t.GetEnd()
    sx, sy = s.x / MM, s.y / MM
    if t.GetNetname() == 'HALL_3V3' and 132 < sx < 139 and 70 < sy < 78:
        lay = 'F' if t.GetLayer() == pcbnew.F_Cu else 'B'
        print(f'HALL {lay} ({sx:.2f},{sy:.2f})->({e.x/MM:.2f},{e.y/MM:.2f})')
    if t.GetNetname() == 'EN_A' and t.GetLayer() == pcbnew.B_Cu and 108 < sx < 125 and 100 < sy < 125:
        print(f'EN_A B ({sx:.2f},{sy:.2f})->({e.x/MM:.2f},{e.y/MM:.2f})')
