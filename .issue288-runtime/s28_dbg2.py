import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
import s24_router
from s24_router import Obstacles, route

s24_router.CLEAR = 0.13
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
obs = Obstacles(b)
nc = b.FindNet('EN_A').GetNetCode()
res = route(obs, (50.25, 90.7, 0), (50.25, 74.7, 0), nc, 0.10)
print('result:', 'OK' if res else 'FAIL')
if res:
    pts, vias = res
    print('points:', [(round(x,2), round(y,2), l) for x, y, l in pts], 'vias:', vias)
