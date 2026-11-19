import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
import s24_router
from s24_router import Obstacles

s24_router.CLEAR = 0.13
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
obs = Obstacles(b)
nc = b.FindNet('EN_A').GetNetCode()
for layer in (0, 1):
    print(f'--- layer {"F" if layer == 0 else "B"}  x=44..58 (1mm), y=70..96 (1mm)')
    for y in range(70, 97):
        row = ''
        for x in range(44, 59):
            row += 'X' if obs.blocked(x + 0.0, y + 0.0, layer, nc, 0.05) else '.'
        print(f'y={y:3d} {row}')
