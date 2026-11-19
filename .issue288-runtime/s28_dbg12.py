import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, _seg_clear

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
obs = Obstacles(b)
nc = b.FindNet('EN_A').GetNetCode()
px, py = 50.25, 74.7
print('south stub clear:', _seg_clear(obs, px, py, px, py + 1.5, 0, nc, 0.05))
# sample the stub line
for k in range(16):
    y = py + k * 0.1
    print(f'  ({px},{y:.1f}) blocked={obs.blocked(px, y, 0, nc, 0.05)}')
# via scan south box
legal = []
vy = py + 1.0
while vy <= py + 4.5:
    vx = px - 2.0
    while vx <= px + 3.0:
        if not (obs.blocked(vx, vy, 0, nc, 0.30, via=True) or obs.blocked(vx, vy, 1, nc, 0.30, via=True)):
            legal.append((round(vx, 2), round(vy, 2)))
        vx += 0.25
    vy += 0.25
print('legal via landings in south box:', legal[:20], 'total', len(legal))
