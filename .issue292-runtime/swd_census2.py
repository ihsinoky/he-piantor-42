"""Census 2: all-layer items in the wider SWD box + outline Y probe."""
import pcbnew as p
from pathlib import Path
from shapely.geometry import LineString
TREE = Path('../hardware/kicad/qualification/issue-292-wmain')
b = p.LoadBoard(str(TREE / 'wmain.kicad_pcb'))
def mm(v): return v / 1e6
BOX = (100.0, 130.0, 121.0, 139.5)

print('== tracks by layer in box ==')
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA): continue
    s, e = t.GetStart(), t.GetEnd()
    pts = [(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]
    if any(BOX[0] <= px <= BOX[2] and BOX[1] <= py <= BOX[3] for px, py in pts):
        print(f"  {t.GetLayerName():7s} {t.GetNetname():10s} {pts[0]}->{pts[1]} w={mm(t.GetWidth()):.3f}")

print('== vias in box ==')
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        pos = t.GetPosition(); x, y = mm(pos.x), mm(pos.y)
        if BOX[0] <= x <= BOX[2] and BOX[1] <= y <= BOX[3]:
            print(f"  VIA {t.GetNetname()} @({x:.3f},{y:.3f}) d={mm(t.GetWidth(p.F_Cu)):.3f}")

print('== zones intersecting box ==')
for z in b.Zones():
    bb = z.GetBoundingBox()
    print('  zone', z.GetNetname(), 'layer', z.GetLayerName(),
          'bbox', tuple(round(mm(v), 2) for v in (bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom())))

print('== outline: board polygon Y extent at given X ==')
ps = p.SHAPE_POLY_SET()
b.GetBoardPolygonOutlines(ps)
out = ps.Outline(0)
pts = []
for i in range(out.PointCount()):
    q = out.CPoint(i); pts.append((mm(q.x), mm(q.y)))
poly = LineString(pts + [pts[0]])
for x in (105.0, 107.69, 110.5, 114.31, 115.31, 116.0):
    from shapely.geometry import LineString as LS
    v = LS([(x, 120.0), (x, 145.0)])
    inter = poly.intersection(v)
    ys = []
    if hasattr(inter, 'geoms'):
        for g in inter.geoms: ys.append(round(g.y, 3))
    elif not inter.is_empty: ys.append(round(inter.y, 3))
    print(f"  X={x}: outline crossings Y={sorted(ys)}")
print('== outline segments near south (Y>135, X 100..125) ==')
for i in range(len(pts)):
    a, c = pts[i], pts[(i + 1) % len(pts)]
    if (100 <= a[0] <= 125 and a[1] > 135) or (100 <= c[0] <= 125 and c[1] > 135):
        print('  ', tuple(round(v, 3) for v in a), '->', tuple(round(v, 3) for v in c))
