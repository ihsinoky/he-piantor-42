import math, sys
from pathlib import Path
import pcbnew
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
MM = 1e6
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
n = 0
for t in list(b.GetTracks()):
    if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() == 'VIN_SRC':
        p = t.GetPosition()
        if math.hypot(p.x / MM - 147.464, p.y / MM - 132.714) < 0.4:
            b.Remove(t); n += 1
b.Save(str(TREE / 'wmatrix.kicad_pcb'))
print('deleted', n, 'bad VIN_SRC via')
