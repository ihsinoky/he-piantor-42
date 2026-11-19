import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s28_component_route import Comp
MM = 1e6
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
comp = Comp(b)
comps = comp.components('H_A0_RAW')
for i, c in enumerate(comps):
    print('comp', i, 'size', len(c))
    for it in c:
        kind = it[0]
        if kind == 'pad':
            print('   pad', it[1], it[2], (round(it[3], 2), round(it[4], 2)))
        elif kind == 'seg':
            print('   seg', (round(it[1], 2), round(it[2], 2)), (round(it[3], 2), round(it[4], 2)), 'L', it[6])
        else:
            print('   via', (round(it[1], 2), round(it[2], 2)))
