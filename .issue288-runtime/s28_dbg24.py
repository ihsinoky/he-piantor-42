import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s28_component_route import Comp

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
comp = Comp(b)
for ci, c in enumerate(comp.components('MUXA_OUT')):
    print(f'--- fragment {ci} ({len(c)} items)')
    for i in c:
        it = comp.items[i]
        if it['kind'] == 'pad':
            print(f"  pad ({it['x']:.2f},{it['y']:.2f})")
        elif it['kind'] == 'via':
            print(f"  via ({it['x']:.2f},{it['y']:.2f})")
        else:
            print(f"  seg L{it['layers']} ({it['ax']:.2f},{it['ay']:.2f})->({it['bx']:.2f},{it['by']:.2f})")
