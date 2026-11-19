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
net = b.FindNet('EN_A')
nc = net.GetNetCode()
# grid of blocked cells around the corridor x 49..52, y 73..92 (F layer, width 0.10)
for y in [74.7, 76.0, 78.0, 80.0, 82.0, 84.0, 86.0, 88.0, 89.3, 90.7]:
    row = ''
    for x in [49.5, 49.75, 50.0, 50.25, 50.5, 50.75, 51.0, 51.5]:
        row += 'X' if obs.blocked(x, y, 0, nc, 0.05) else '.'
    print(f'y={y:6.2f}  {row}   (x=49.5..51.5 step .25)')
# what pads are near (50.25, 82)?
print('pads near corridor:')
for (px, py, r, pnc, on_f, on_b) in obs.pads:
    if abs(px - 50.25) < 3 and 72 < py < 93:
        print(f'  pad ({px:.2f},{py:.2f}) r={r:.3f} netcode={pnc} F={on_f} B={on_b}')
print('EN_A netcode:', nc)
