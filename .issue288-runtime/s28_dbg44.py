import sys
from pathlib import Path
import pcbnew
MM = 1e6
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
for t in list(b.GetTracks()):
    if t.GetNetname() != 'H_B3_RAW':
        continue
    if t.Type() == pcbnew.PCB_VIA_T:
        p = t.GetPosition()
        if 95 < p.x / MM < 100 and 111 < p.y / MM < 116:
            print(f'VIA ({p.x/MM:.2f},{p.y/MM:.2f})')
    else:
        s, e = t.GetStart(), t.GetEnd()
        if (95 < s.x / MM < 100 and 111 < s.y / MM < 116) or (95 < e.x / MM < 100 and 111 < e.y / MM < 116):
            lay = 'F' if t.GetLayer() == pcbnew.F_Cu else 'B'
            print(f'{lay} ({s.x/MM:.3f},{s.y/MM:.3f})->({e.x/MM:.3f},{e.y/MM:.3f})')
