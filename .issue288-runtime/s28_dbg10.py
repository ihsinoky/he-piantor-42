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
for sx in (1, -1):
    ex = px + sx * 1.25
    print(f'sx={sx} stub clear:', _seg_clear(obs, px, py, ex, py, 0, nc, 0.05))
    ok = 0
    for dy in (1.0, 1.5, 2.0, 2.5, 3.0, 0.5, 3.5):
        for dx in (1.25, 1.75, 2.25, 2.75, 0.75):
            vx, vy = px + sx * dx, py + dy
            vf = obs.blocked(vx, vy, 0, nc, 0.30, via=True)
            vb = obs.blocked(vx, vy, 1, nc, 0.30, via=True)
            dg = _seg_clear(obs, ex, py, vx, vy, 0, nc, 0.05)
            if not (vf or vb) and dg:
                print(f'  LEGAL via ({vx:.2f},{vy:.2f})')
                ok += 1
    print(f'  legal candidates: {ok}')
