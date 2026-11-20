import math, sys
from pathlib import Path
import pcbnew
MM = 1e6
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
for t in list(b.GetTracks()):
    if t.Type() != pcbnew.PCB_TRACE_T or t.GetNetname() != 'H_A5_RAW':
        continue
    s, e = t.GetStart(), t.GetEnd()
    if 114 < s.x / MM < 121 and 103 < s.y / MM < 112:
        lay = 'F' if t.GetLayer() == pcbnew.F_Cu else 'B'
        print(f'{lay} ({s.x/MM:.3f},{s.y/MM:.3f})->({e.x/MM:.3f},{e.y/MM:.3f})')
