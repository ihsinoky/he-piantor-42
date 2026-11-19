import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, _seg_clear

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
obs = Obstacles(b)
nc = b.FindNet('H_B3_RAW').GetNetCode()
pts = [(134.25, 72.3), (135.0, 71.9), (136.5, 72.5), (136.5, 74.3), (134.25, 74.3)]
for a, c in zip(pts, pts[1:]):
    print(a, '->', c, _seg_clear(obs, a[0], a[1], c[0], c[1], 0, nc, 0.05))
nc2 = b.FindNet('EN_A').GetNetCode()
print('HA5 SE stub:', _seg_clear(obs, 117.25, 107.7, 117.75, 108.2, 0, nc2, 0.05))
for (x, y) in [(117.4, 107.85), (117.6, 108.05), (117.75, 108.2)]:
    print((x, y), 'EN_A blocked:', obs.blocked(x, y, 0, nc2, 0.05))
