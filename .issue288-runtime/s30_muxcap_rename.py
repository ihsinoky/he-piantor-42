import sys
from pathlib import Path
import pcbnew
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
BOARD = TREE / 'wmatrix.kicad_pcb'
b = pcbnew.LoadBoard(str(BOARD))
ren = {'C_MUX_A': 'C_MUXA', 'C_MUX_B': 'C_MUXB', 'C_MUX_C': 'C_MUXC'}
n = 0
for fp in list(b.GetFootprints()):
    if fp.GetReference() in ren:
        fp.SetReference(ren[fp.GetReference()])
        n += 1
b.Save(str(BOARD))
print('renamed', n)
