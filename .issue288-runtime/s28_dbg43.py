import math, sys
from pathlib import Path
import pcbnew
MM = 1e6
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
nv = ns = 0
for t in list(b.GetTracks()):
    if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() == 'EN_B':
        p = t.GetPosition()
        if math.hypot(p.x / MM - 97.12, p.y / MM - 113.45) < 0.05:
            nv += 1
    if t.Type() == pcbnew.PCB_TRACE_T and t.GetNetname() == 'H_B3_RAW':
        s = t.GetStart()
        if math.hypot(s.x / MM - 97.562357, s.y / MM - 113.344432) < 0.05:
            ns += 1
            e = t.GetEnd()
            print('  stub ->', (round(e.x / MM, 3), round(e.y / MM, 3)), 'len', round(t.GetLength() / MM, 4))
print('EN_B vias at spot:', nv, 'HB3 stubs at spot:', ns)
