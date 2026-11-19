import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, route

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
obs = Obstacles(b)
nc = b.FindNet('REF_RAIL').GetNetCode()
src = (84.932075, 124.275, 0)
for name, dst in {'MUXB pin9 pad': (102.932075, 124.275, 0),
                  'MUXC pin9 pad': (120.932075, 124.275, 0),
                  'stub pt (103.65,123.99)': (103.646847, 123.989772, 0)}.items():
    res = route(obs, src, dst, nc, 0.10)
    print(name, '->', 'OK' if res else 'FAIL')
