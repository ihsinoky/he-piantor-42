import sys
from pathlib import Path
import pcbnew
MM = 1e6
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
for fp in list(b.GetFootprints()):
    p = fp.GetPosition()
    if 118 < p.y / MM < 126 and 80 < p.x / MM < 130:
        nets = [pad.GetNetname() for pad in fp.Pads()]
        print(fp.GetReference(), (round(p.x / MM, 2), round(p.y / MM, 2)), fp.GetFPID().GetLibItemName(), nets)
