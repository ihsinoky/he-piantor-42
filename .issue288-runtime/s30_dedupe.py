import sys
from pathlib import Path
import pcbnew

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
BOARD = TREE / 'wmatrix.kicad_pcb'
MM = 1e6
b = pcbnew.LoadBoard(str(BOARD))
seen = {}
removed = 0
for t in list(b.GetTracks()):
    if t.Type() != pcbnew.PCB_VIA_T:
        continue
    p = t.GetPosition()
    key = (t.GetNetCode(), round(p.x / MM, 3), round(p.y / MM, 3))
    if key in seen:
        b.Remove(t)
        removed += 1
    else:
        seen[key] = t
b.Save(str(BOARD))
print('duplicate vias removed:', removed)
