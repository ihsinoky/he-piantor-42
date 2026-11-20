import math, sys
from pathlib import Path
import pcbnew
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
BOARD = TREE / 'wmatrix.kicad_pcb'
MM = 1e6
b = pcbnew.LoadBoard(str(BOARD))
n = 0
for t in list(b.GetTracks()):
    if t.Type() != pcbnew.PCB_TRACE_T or t.GetNetname() != 'H_B3_RAW' or t.GetLayer() != pcbnew.F_Cu:
        continue
    s, e = t.GetStart(), t.GetEnd()
    mx, my = (s.x + e.x) / 2 / MM, (s.y + e.y) / 2 / MM
    if math.hypot(mx - 97.3, my - 113.5) < 0.7:
        b.Remove(t); n += 1
b.Save(str(BOARD))
print('deleted', n)
