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
nets = ['GND', 'HALL_3V3', 'H_A0_RAW', 'H_B2_RAW', 'H_B3_RAW', 'H_B4_RAW',
        'H_C0_RAW', 'H_C1_RAW', 'MUX_A0', 'MUX_A1', 'MUX_A2', 'VIN_SRC']
for net in nets:
    for attempt in range(4):
        obs = Obstacles(b)
        comp = Comp(b)
        comps = comp.components(net)
        if len(comps) <= 1:
            break
        if not try_connect(b, obs, comp, net, comps):
            print(net, 'attempt', attempt, 'FAILED, comps', [len(c) for c in comps])
            break
    else:
        pass
    comp = Comp(b)
    print(net, 'final comps:', [len(c) for c in comp.components(net)])
b.Save(str(BOARD))
print('saved')
