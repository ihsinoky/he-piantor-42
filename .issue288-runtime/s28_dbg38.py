import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s28_component_route import Comp
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
comp = Comp(b)
comps = comp.components('H_A0_RAW')
for i, c in enumerate(comps):
    print('comp', i, 'size', len(c))
    for idx in c:
        it = comp.items[idx]
        if it['kind'] == 'pad':
            print('   pad', (round(it['x'], 2), round(it['y'], 2)))
        elif it['kind'] == 'seg':
            print('   seg', (round(it['ax'], 2), round(it['ay'], 2)), (round(it['bx'], 2), round(it['by'], 2)), 'F' if it['layers'][0] else 'B')
        else:
            print('   via', (round(it['x'], 2), round(it['y'], 2)))
