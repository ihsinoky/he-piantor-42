import pcbnew as p, math
from shapely.geometry import Point, LineString, Polygon
from shapely.strtree import STRtree
b = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
def mm(v): return v/1e6
for f in b.GetFootprints():
    if f.GetReference() == 'J3':
        for pad in f.Pads():
            if pad.GetNumber() == '10':
                q = pad.GetPosition(); sz = pad.GetSize()
                print('pad10 pos', mm(q.x), mm(q.y), 'size', mm(sz.x), mm(sz.y), 'rot', pad.GetOrientationDegrees(), 'shape', pad.GetShape(), 'net', pad.GetNetname())
                cx, cy = mm(q.x), mm(q.y)
                rot = math.radians(pad.GetOrientationDegrees())
                c, s = math.cos(rot), math.sin(rot)
                w, h = mm(sz.x), mm(sz.y)
                poly = Polygon([(cx + dx*c - dy*s, cy + dx*s + dy*c) for dx, dy in ((-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2))])
                print('poly bounds', poly.bounds)
                n = 0
                for t in b.GetTracks():
                    if t.GetNetname() != 'MUX_A1': continue
                    if isinstance(t, p.PCB_VIA):
                        qq = t.GetPosition(); sh = Point(mm(qq.x), mm(qq.y)).buffer(0.3)
                    else:
                        ss, ee = t.GetStart(), t.GetEnd()
                        sh = LineString([(mm(ss.x), mm(ss.y)), (mm(ee.x), mm(ee.y))]).buffer(mm(t.GetWidth())/2)
                    if sh.intersects(poly): n += 1
                print('intersecting MUX_A1 items:', n)
