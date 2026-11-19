import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles
from s28_component_route import Comp
from s29_finish import try_connect

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
BOARD = TREE / 'wmatrix.kicad_pcb'
b = pcbnew.LoadBoard(str(BOARD))
for attempt in range(3):
    obs = Obstacles(b)
    comp = Comp(b)
    comps = comp.components('H_B3_RAW')
    print('comps:', [len(c) for c in comps])
    if len(comps) <= 1:
        break
    if not try_connect(b, obs, comp, 'H_B3_RAW', comps):
        print('FAILED')
        break
    b.Save(str(BOARD))
    b = pcbnew.LoadBoard(str(BOARD))
comp = Comp(b)
print('final:', [len(c) for c in comp.components('H_B3_RAW')])
