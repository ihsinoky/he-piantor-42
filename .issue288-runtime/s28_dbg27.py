import sys
from pathlib import Path
import pcbnew
MM = 1e6
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
for t in list(b.GetTracks()):
    if t.GetNetname() not in ('H_B3_RAW', 'EN_C', 'H_C5_RAW'):
        continue
    if t.Type() == pcbnew.PCB_VIA_T:
        p = t.GetPosition()
        print(f'{t.GetNetname()} VIA ({p.x/MM:.2f},{p.y/MM:.2f})')
    else:
        s, e = t.GetStart(), t.GetEnd()
        if 125 < s.x / MM < 165 and 65 < s.y / MM < 125:
            lay = 'F' if t.GetLayer() == pcbnew.F_Cu else 'B'
            print(f'{t.GetNetname()} {lay} ({s.x/MM:.2f},{s.y/MM:.2f})->({e.x/MM:.2f},{e.y/MM:.2f})')
