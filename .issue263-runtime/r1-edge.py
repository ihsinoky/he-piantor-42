"""R1: inspect Edge.Cuts drawings near the west edge for each Wing variant."""
import pcbnew as p
from pathlib import Path
E = Path('/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation')
for name in ('wing-rev5-17mm-right', 'wing-rev5-16mm-right'):
    b = p.LoadBoard(str(E / name / 'routed.kicad_pcb'))
    print(f'== {name}')
    for d in b.GetDrawings():
        if d.GetLayer() != p.Edge_Cuts:
            continue
        t = d.Type()
        if t == p.PCB_SHAPE_T:
            s, e = d.GetStart(), d.GetEnd()
            x0, y0, x1, y1 = p.ToMM(s.x), p.ToMM(s.y), p.ToMM(e.x), p.ToMM(e.y)
            if min(x0, x1) < 45 and max(y0, y1) > 80 and min(y0, y1) < 112:
                print(f'  shape type {d.GetShape()} ({x0:.2f},{y0:.2f})->({x1:.2f},{y1:.2f})', flush=True)
print('done')
