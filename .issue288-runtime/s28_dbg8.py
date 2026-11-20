import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
import s24_router
from s24_router import Obstacles

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
obs = Obstacles(b)
nc = b.FindNet('GND').GetNetCode()
for layer in (0, 1):
    print(f'--- layer {"F" if layer == 0 else "B"}: x 76..82 step 0.5, y 116..124 step 0.5 (S=(79.07,121.03) G=(78.25,118.4))')
    y = 116.0
    while y <= 124.01:
        row = ''
        x = 76.0
        while x <= 82.01:
            row += 'X' if obs.blocked(x, y, layer, nc, 0.15) else '.'
            x += 0.5
        print(f'y={y:6.2f} {row}')
        y += 0.5
