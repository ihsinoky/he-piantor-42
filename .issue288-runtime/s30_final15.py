import math, sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s28_component_route import Comp

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
BOARD = TREE / 'wmatrix.kicad_pcb'
MM = 1e6
step = sys.argv[1]
b = pcbnew.LoadBoard(str(BOARD))
if step == 'del':
    n = 0
    for t in list(b.GetTracks()):
        if t.Type() != pcbnew.PCB_TRACE_T or t.GetNetname() != 'H_B3_RAW':
            continue
        s, e = t.GetStart(), t.GetEnd()
        if math.hypot(s.x / MM - 97.562357, s.y / MM - 113.344432) < 0.35 or \
           math.hypot(e.x / MM - 97.562357, e.y / MM - 113.344432) < 0.35:
            b.Remove(t); n += 1
    b.Save(str(BOARD))
    print('deleted', n)
elif step == 'info':
    comp = Comp(b)
    comps = comp.components('H_B3_RAW')
    print('comps:', [len(c) for c in comps])
    small = min(comps, key=len)
    for idx in small:
        it = comp.items[idx]
        if it['kind'] == 'pad':
            print('   pad', (round(it['x'], 2), round(it['y'], 2)))
        elif it['kind'] == 'seg':
            print('   seg', (round(it['ax'], 2), round(it['ay'], 2)), (round(it['bx'], 2), round(it['by'], 2)), 'F' if it['layers'][0] else 'B')
        else:
            print('   via', (round(it['x'], 2), round(it['y'], 2)))
