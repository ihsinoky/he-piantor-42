"""R2 verify: outline area of respin-in vs pre-respin backup per variant."""
import pcbnew as p
from pathlib import Path
RT = Path('/home/hatch/workspace/projects/he-piantor-boards/.issue263-runtime')
E = Path('/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation')

def area(fn):
    b = p.LoadBoard(str(fn))
    poly = p.SHAPE_POLY_SET()
    b.GetBoardPolygonOutlines(poly)
    return poly.Area() / 1e12, poly.OutlineCount()

for name in ('wing-rev5-16mm-left', 'wing-rev5-16mm-right', 'wing-rev5-17mm-left', 'wing-rev5-17mm-right'):
    a0, n0 = area(RT / 'board-backup' / 'respin-pre' / name / 'main.kicad_pcb')
    a1, n1 = area(E / name / 'respin-in.kicad_pcb')
    print(f'{name}: outlines {n0}->{n1}, area {a0:.1f} -> {a1:.1f} mm2 (delta {a1-a0:+.1f})', flush=True)
print('done')
