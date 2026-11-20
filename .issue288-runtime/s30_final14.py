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
    comps = comp.components('GND')
    if len(comps) <= 1:
        break
    if not try_connect(b, obs, comp, 'GND', comps):
        print('FAILED', [len(c) for c in comps])
        break
    b.Save(str(BOARD))
    b = pcbnew.LoadBoard(str(BOARD))
comp = Comp(b)
print('GND comps:', [len(c) for c in comp.components('GND')])
