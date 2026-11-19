import pcbnew as p
from shapely.geometry import Point, Polygon
b = p.LoadBoard('.issue292-runtime/wmain-work.kicad_pcb')
def mm(v): return v / 1e6
polys = []
for z in b.Zones():
    if z.GetNetname() != 'GND' or z.GetLayer() != 4: continue
    fp_ = z.GetFilledPolysList(4)
    for i in range(fp_.OutlineCount()):
        ch = fp_.Outline(i)
        pts = [(mm(ch.CPoint(j).x), mm(ch.CPoint(j).y)) for j in range(ch.PointCount())]
        if len(pts) >= 3: polys.append(Polygon(pts))
print('In1 polys:', len(polys), 'total area', round(sum(pg.area for pg in polys), 1))
for y in (94.0, 95.5, 97.0, 98.5, 100.0, 101.5):
    row = ''
    for x in (106.0, 108.0, 110.0, 112.0, 114.0, 116.0):
        row += 'Y' if any(pg.contains(Point(x, y)) for pg in polys) else '.'
    print('y', y, row)
for q in [(112.6, 98.3), (107.87, 97.12), (107.7, 97.25)]:
    print(q, any(pg.contains(Point(*q)) for pg in polys))
