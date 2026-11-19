import pcbnew as p
from shapely.geometry import LineString, Point
def mm(v): return v / 1e6
b = p.LoadBoard('.issue292-runtime/wmain-work.kicad_pcb')
for t in b.GetTracks():
    if t.GetNetname() != 'MUX_A0' or isinstance(t, p.PCB_VIA): continue
    s, e = t.GetStart(), t.GetEnd()
    a, bb = (round(mm(s.x), 2), round(mm(s.y), 2)), (round(mm(e.x), 2), round(mm(e.y), 2))
    if {a, bb} == {(72.10, 123.41), (72.05, 125.55)}:
        print('width now', mm(t.GetWidth()))
        g = LineString([(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]).buffer(mm(t.GetWidth()) / 2, quad_segs=8)
        print('dist to DP via disc', round(g.distance(Point(72.43, 124.85).buffer(0.3, quad_segs=24)), 4))
