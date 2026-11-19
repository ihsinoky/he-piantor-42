import math, sys
from pathlib import Path
import pcbnew
MM = 1e6
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
for t in list(b.GetTracks()):
    if t.GetNetname() != 'MUXA_OUT':
        continue
    if t.Type() == pcbnew.PCB_VIA_T:
        p = t.GetPosition()
        print(f'VIA ({p.x/MM:.2f},{p.y/MM:.2f})')
    else:
        s, e = t.GetStart(), t.GetEnd()
        L = math.hypot(e.x - s.x, e.y - s.y) / MM
        if 76 < s.x / MM < 90 and 121 < s.y / MM < 130:
            lay = 'F' if t.GetLayer() == pcbnew.F_Cu else 'B'
            print(f'{lay} ({s.x/MM:.2f},{s.y/MM:.2f})->({e.x/MM:.2f},{e.y/MM:.2f}) L={L:.3f}')
