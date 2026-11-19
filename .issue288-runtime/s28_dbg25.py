import sys
from pathlib import Path
import pcbnew
MM = 1e6
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
for t in list(b.GetTracks()):
    if t.GetNetname() != 'VIN_SRC':
        continue
    if t.Type() == pcbnew.PCB_VIA_T:
        p = t.GetPosition()
        if p.x / MM > 140:
            print(f'VIA ({p.x/MM:.2f},{p.y/MM:.2f})')
    else:
        s, e = t.GetStart(), t.GetEnd()
        if s.x / MM > 140 and s.y / MM > 125:
            lay = 'F' if t.GetLayer() == pcbnew.F_Cu else 'B'
            print(f'{lay} ({s.x/MM:.2f},{s.y/MM:.2f})->({e.x/MM:.2f},{e.y/MM:.2f})')
