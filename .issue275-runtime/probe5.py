"""What encloses new pad 5 (GND at mirror of J3 pad 11 = (73.7833,112.286))?
List all copper within 2.2mm of that point in the Rev.9 board, excluding
segments that touch OLD J2 pads (those get deleted)."""
import math
from pathlib import Path
import pcbnew as p
from shapely.geometry import LineString, Point, Polygon

MM = 1e6
SRC = Path("/home/hatch/workspace/projects/he-piantor-mainsym/hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb")
b = p.LoadBoard(str(SRC))
C = Point(73.7833, 112.286)

def pad_poly(a):
    sh = a.GetEffectiveShape(p.F_Cu)
    ps = p.SHAPE_POLY_SET()
    sh.TransformToPolygon(ps, 0, p.ERROR_OUTSIDE)
    out = ps.Outline(0)
    return Polygon([(out.GetPoint(i).x / MM, out.GetPoint(i).y / MM) for i in range(out.PointCount())])

fp = b.FindFootprintByReference("J2")
old_rects = []
for a in fp.Pads():
    if a.GetNumber() != "MP":
        old_rects.append(pad_poly(a).buffer(0.03, join_style=2))

for t in b.GetTracks():
    s, e = t.GetStart(), t.GetEnd()
    ls = LineString([(s.x / MM, s.y / MM), (e.x / MM, e.y / MM)])
    d = ls.distance(C)
    if d < 2.2:
        w = (t.GetWidth(p.F_Cu) if isinstance(t, p.PCB_VIA) else t.GetWidth()) / MM
        touches_old = any(ls.intersects(r) for r in old_rects)
        print(f"{'via' if isinstance(t, p.PCB_VIA) else 'trk'} {t.GetNetname():<10} L{t.GetLayer()} w={w:.2f} d={d:.3f} "
              f"({s.x/MM:.2f},{s.y/MM:.2f})->({e.x/MM:.2f},{e.y/MM:.2f}) {'DELETED' if touches_old else ''}")
for f in b.GetFootprints():
    for a in f.Pads():
        if a.IsOnLayer(p.F_Cu):
            pp = a.GetPosition()
            if math.hypot(pp.x / MM - C.x, pp.y / MM - C.y) < 2.6:
                print("pad", f.GetReference(), a.GetNumber(), a.GetNetname(), (round(pp.x / MM, 3), round(pp.y / MM, 3)),
                      "d=", round(pad_poly(a).distance(C), 3))
