"""Locate every cross-net copper overlap/touch in the work board with exact
shapes, classifying each item as ORIGINAL (uuid in tree board) or NEW."""
import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
import pcbnew as p
from shapely.strtree import STRtree

tree = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
orig_uuids = set()
for t in tree.GetTracks(): orig_uuids.add(t.m_Uuid.AsString())
for f in tree.GetFootprints():
    for pad in f.Pads(): orig_uuids.add(pad.m_Uuid.AsString())

work = p.LoadBoard(DST)
items = []  # (net, layer, shape, desc, is_new)
def rect_poly2(cx, cy, w, h, rot):
    import math as m
    c, s = m.cos(m.radians(rot)), m.sin(m.radians(rot))
    from shapely.geometry import Polygon
    return Polygon([(cx + dx * c + dy * s, cy - dx * s + dy * c)
                    for dx, dy in ((-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2))])
for f in work.GetFootprints():
    for pad in f.Pads():
        q = pad.GetPosition(); sz = pad.GetSize()
        if pad.GetShape() == p.PAD_SHAPE_CIRCLE:
            sh = Point(mm(q.x), mm(q.y)).buffer(mm(sz.x) / 2, quad_segs=16)
        else:
            sh = rect_poly2(mm(q.x), mm(q.y), mm(sz.x), mm(sz.y), pad.GetOrientationDegrees())
        for L in LAYERS:
            if pad.IsOnLayer(LC[L]) or pad.GetAttribute() == p.PAD_ATTRIB_PTH:
                items.append((pad.GetNetname(), L, sh,
                              f"pad {f.GetReference()}.{pad.GetNumber()}",
                              pad.m_Uuid.AsString() not in orig_uuids))
for t in work.GetTracks():
    new = t.m_Uuid.AsString() not in orig_uuids
    if isinstance(t, p.PCB_VIA):
        q = t.GetPosition()
        for L in LAYERS:
            items.append((t.GetNetname(), L, Point(mm(q.x), mm(q.y)).buffer(mm(t.GetWidth(LC[L])) / 2, quad_segs=16),
                          f"via @({mm(q.x):.2f},{mm(q.y):.2f})", new))
    else:
        L = {p.F_Cu: 'F', p.In2_Cu: 'I2', p.B_Cu: 'B'}.get(t.GetLayer())
        if L:
            s, e = t.GetStart(), t.GetEnd()
            sh = LineString([(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]).buffer(mm(t.GetWidth()) / 2, quad_segs=6)
            items.append((t.GetNetname(), L, sh,
                          f"trk ({mm(s.x):.2f},{mm(s.y):.2f})-({mm(e.x):.2f},{mm(e.y):.2f})", new))
for L in LAYERS:
    layer_items = [it for it in items if it[1] == L]
    tree_q = STRtree([it[2] for it in layer_items])
    for i, (n1, _, s1, d1, new1) in enumerate(layer_items):
        for j in tree_q.query(s1, predicate='intersects'):
            if j <= i: continue
            n2, _, s2, d2, new2 = layer_items[j]
            if n1 == n2 or not n1 or not n2: continue
            inter = s1.intersection(s2)
            if inter.area > 1e-6:
                c = inter.centroid
                print(f'{L} SHORT {n1} x {n2} area={inter.area:.3f} @({c.x:.2f},{c.y:.2f}) | {d1} [{"NEW" if new1 else "orig"}] x {d2} [{"NEW" if new2 else "orig"}]')
print('done')
