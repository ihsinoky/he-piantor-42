import heapq, math, sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
import s24_router
from s24_router import Obstacles, _astar

s24_router.CLEAR = 0.13
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
obs = Obstacles(b)
nc = b.FindNet('EN_A').GetNetCode()
# window like route(): margin 12
res = _astar(obs, (50.25, 90.7, 0), (50.25, 74.7, 0), nc, 0.10, 38.25, 62.25, 62.7, 102.7)
print('windowed:', 'OK' if res else 'FAIL')
res2 = _astar(obs, (50.25, 90.7, 0), (50.25, 74.7, 0), nc, 0.10,
              obs.bbox[0] + 0.2, obs.bbox[2] - 0.2, obs.bbox[1] + 0.2, obs.bbox[3] - 0.2)
print('fullboard:', 'OK' if res2 else 'FAIL')
# check blocked() along a hand path: south exit then west then north at x=47
for (x, y) in [(50.25, 91.5), (49.0, 92.5), (47.0, 92.0), (47.0, 85.0), (47.0, 78.0), (48.5, 75.5), (50.25, 74.7)]:
    print((x, y), 'blocked F:', obs.blocked(x, y, 0, nc, 0.05))
