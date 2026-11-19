import math, sys
from pathlib import Path
import pcbnew
MM = 1e6
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
for ref in ('R_SHUNT', 'C_LDO_OUT'):
    for fp in list(b.GetFootprints()):
        if fp.GetReference() == ref:
            for pad in fp.Pads():
                pp = pad.GetPosition()
                print(ref, 'pad', pad.GetNumber(), pad.GetNetname(), (round(pp.x / MM, 3), round(pp.y / MM, 3)))
targets = [(120.156, 130.0), (121.844, 130.0)]
for (tx, ty) in targets:
    hits = []
    for t in list(b.GetTracks()):
        if t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            if math.hypot(p.x / MM - tx, p.y / MM - ty) < 0.01:
                hits.append(('via', t.GetNetname()))
        else:
            s, e = t.GetStart(), t.GetEnd()
            for p in (s, e):
                if math.hypot(p.x / MM - tx, p.y / MM - ty) < 0.01:
                    hits.append(('seg', t.GetNetname()))
    print((tx, ty), 'endpoint touches:', hits)
