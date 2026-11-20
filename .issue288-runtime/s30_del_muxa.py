import math, sys
from pathlib import Path
import pcbnew
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
MM = 1e6
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
tracks = list(b.GetTracks())
n = 0
for t in tracks:
    if t.Type() == pcbnew.PCB_TRACE_T and t.GetNetname() == 'MUXA_OUT':
        s = t.GetStart()
        if math.hypot(s.x / MM - 78.2, s.y / MM - 123.8) < 0.3:
            b.Remove(t)
            n += 1
b.Save(str(TREE / 'wmatrix.kicad_pcb'))
print('deleted', n, 'grazing MUXA_OUT segments; saved')
