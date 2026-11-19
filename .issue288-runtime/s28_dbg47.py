import math, sys
from pathlib import Path
import pcbnew
MM = 1e6
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
for fp in list(b.GetFootprints()):
    if fp.GetReference() == 'U_HA0':
        for pad in fp.Pads():
            pp = pad.GetPosition()
            print('U_HA0 pad', pad.GetNumber(), pad.GetNetname(), (round(pp.x / MM, 3), round(pp.y / MM, 3)))
tx, ty = 49.75, 73.3
for t in list(b.GetTracks()):
    if t.Type() == pcbnew.PCB_VIA_T:
        p = t.GetPosition()
        if math.hypot(p.x / MM - tx, p.y / MM - ty) < 2.0:
            print('VIA', t.GetNetname(), (round(p.x / MM, 2), round(p.y / MM, 2)))
    else:
        s, e = t.GetStart(), t.GetEnd()
        for (qx, qy) in [(s.x / MM, s.y / MM), (e.x / MM, e.y / MM)]:
            if math.hypot(qx - tx, qy - ty) < 2.0:
                lay = 'F' if t.GetLayer() == pcbnew.F_Cu else 'B'
                print('SEG', t.GetNetname(), lay, (round(s.x / MM, 2), round(s.y / MM, 2)), (round(e.x / MM, 2), round(e.y / MM, 2)))
                break
