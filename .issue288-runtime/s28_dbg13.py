import math, sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, _seg_clear

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
obs = Obstacles(b)
nc = b.FindNet('EN_A').GetNetCode()
px, py = 50.25, 74.7
landings = []
vy = py - 1.5
while vy <= py + 5.0:
    vx = px - 2.5
    while vx <= px + 3.5:
        if not (obs.blocked(vx, vy, 0, nc, 0.30, via=True) or obs.blocked(vx, vy, 1, nc, 0.30, via=True)):
            landings.append((math.hypot(vx - px, vy - py), round(vx, 2), round(vy, 2)))
        vx += 0.25
    vy += 0.25
landings.sort()
print('landings total:', len(landings))
print('nearest 15:', landings[:15])
stubs = [(px, py + 1.5), (px + 1.25, py), (px - 1.25, py), (px, py - 1.0)]
for _, vx, vy in landings[:15]:
    direct = _seg_clear(obs, px, py, vx, vy, 0, nc, 0.05)
    via_stub = [(_seg_clear(obs, px, py, sx, sy, 0, nc, 0.05),
                 _seg_clear(obs, sx, sy, vx, vy, 0, nc, 0.05)) for (sx, sy) in stubs]
    print(f'  via ({vx},{vy}) direct={direct} stubshapes={via_stub}')
