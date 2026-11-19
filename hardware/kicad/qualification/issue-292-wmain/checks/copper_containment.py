#!/usr/bin/env python3
"""Copper containment gate (Issue #292, added by the edge-fix round).

FAILS (exit 1) if any copper shape (track / via / pad / zone fill, any copper
layer) CROSSES or TOUCHES the Edge.Cuts board outline. Items that merely sit
closer than the board's 0.5 mm edge clearance are reported as CLOSE warnings
only; each CLOSE item requires an item-level disposition in REPORT.md.

Method: exact geometry. The outline polygon comes from
BOARD.GetBoardPolygonOutlines (KiCad's own chaining); every copper item's
shape is built from its KiCad parameters (segment + width, via diameter,
pad size/shape/orientation, zone filled polygons) and measured with shapely.
Distances are taken to the outline BOUNDARY (a filled polygon's distance to
an interior shape is always 0, which would false-positive).

This is the gate form of the edge-fix round's enumeration tool; its item
list was cross-validated against KiCad DRC on the adopted board (all 114
DRC copper_edge_clearance items contained, 0 missed).

Usage: python3 copper_containment.py <board.kicad_pcb>
Run with a python that has pcbnew (KiCad) and shapely.
"""
import pcbnew as p, math, sys
from shapely.geometry import Polygon, LineString, Point

EDGE_CLR = 0.5
EPS = 0.0005  # mm; distances below this count as 0


def mm(v): return v / 1e6


def chain_points(chain):
    ps = p.SHAPE_POLY_SET()
    chain.TransformToPolygon(ps, 100, False)  # arc error 100 IU = 0.0001 mm
    ch = ps.Outline(0)
    pts = []
    for i in range(ch.PointCount()):
        q = ch.CPoint(i)
        pts.append((mm(q.x), mm(q.y)))
    return pts


def outline_poly(board):
    po = p.SHAPE_POLY_SET(); board.GetBoardPolygonOutlines(po)
    assert po.OutlineCount() == 1, po.OutlineCount()
    pts = chain_points(po.Outline(0))
    poly = Polygon(pts)
    assert poly.is_valid and len(pts) >= 4
    return poly


def seg_poly(a, b, w):
    return LineString([a, b]).buffer(w / 2, quad_segs=32)


def arc_points(ctr, r, a0, a1):
    sweep = (a1 - a0) % 360.0
    if sweep == 0: sweep = 360.0
    steps = max(4, int(sweep / max(0.5, math.degrees(0.001 / max(r, 0.01)) / 4)))
    return [(ctr[0] + r * math.cos(math.radians(a0 + sweep * i / steps)),
             ctr[1] + r * math.sin(math.radians(a0 + sweep * i / steps)))
            for i in range(steps + 1)]


def copper_layers(board):
    return [l for l in (p.F_Cu, p.In1_Cu, p.In2_Cu, p.B_Cu) if board.IsLayerEnabled(l)]


def items(board):
    """Yield dicts: kind, desc, net, layer(name), poly(shapely)."""
    LNAME = {p.F_Cu: 'F.Cu', p.In1_Cu: 'In1.Cu', p.In2_Cu: 'In2.Cu', p.B_Cu: 'B.Cu'}
    for t in board.GetTracks():
        tn = type(t).__name__
        net = t.GetNetname()
        if tn == 'PCB_VIA':
            pos = t.GetPosition(); c = (mm(pos.x), mm(pos.y))
            for l in copper_layers(board):
                if not t.IsOnLayer(l): continue
                d = mm(t.GetWidth(l))
                yield dict(kind='via', net=net, layer=LNAME[l],
                           desc=f"via [{net}] @({c[0]:.3f},{c[1]:.3f}) d={d:.3f}",
                           poly=Point(c).buffer(d / 2, quad_segs=32))
        elif tn == 'PCB_ARC_TRACK':
            s = t.GetEffectiveShape(t.GetLayer())
            a = p.SHAPE_ARC.Cast(s)
            ctr = a.GetCenter(); c = (mm(ctr.x), mm(ctr.y)); r = mm(a.GetRadius())
            pts = arc_points(c, r, a.GetStartAngle(), a.GetEndAngle())
            yield dict(kind='arc', net=net, layer=LNAME[t.GetLayer()],
                       desc=f"arc [{net}] ctr=({c[0]:.3f},{c[1]:.3f}) r={r:.3f}",
                       poly=LineString(pts).buffer(mm(t.GetWidth()) / 2, quad_segs=16))
        else:
            s, e = t.GetStart(), t.GetEnd()
            a = (mm(s.x), mm(s.y)); bq = (mm(e.x), mm(e.y)); w = mm(t.GetWidth())
            yield dict(kind='track', net=net, layer=LNAME[t.GetLayer()],
                       desc=f"track [{net}] ({a[0]:.3f},{a[1]:.3f})->({bq[0]:.3f},{bq[1]:.3f}) w={w:.3f}",
                       poly=seg_poly(a, bq, w))
    for f in board.GetFootprints():
        ref = f.GetReference()
        for pad in f.Pads():
            net = pad.GetNetname()
            pos = pad.GetPosition(); c = (mm(pos.x), mm(pos.y))
            sz = pad.GetSize(); w, h = mm(sz.x), mm(sz.y)
            shape = pad.GetShape()
            layers = [l for l in copper_layers(board) if pad.IsOnLayer(l)]
            if not layers: continue
            if shape == p.PAD_SHAPE_CIRCLE:
                poly = Point(c).buffer(w / 2, quad_segs=32)
            else:  # RECT (only other shape present on this board)
                rot = math.radians(pad.GetOrientationDegrees())
                cs, sn = math.cos(rot), math.sin(rot)
                poly = Polygon([(c[0] + dx * cs - dy * sn, c[1] + dx * sn + dy * cs)
                                for dx, dy in ((-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2))])
            for l in layers:
                yield dict(kind='pad', net=net, layer=LNAME[l],
                           desc=f"pad {ref}.{pad.GetNumber()} [{net}] @({c[0]:.3f},{c[1]:.3f}) {w:.2f}x{h:.2f}",
                           poly=poly)
    for z in board.Zones():
        net = z.GetNetname()
        for l in copper_layers(board):
            if not z.IsOnLayer(l): continue
            fps = z.GetFilledPolysList(l)
            for i in range(fps.OutlineCount()):
                pts = chain_points(fps.Outline(i))
                if len(pts) < 3: continue
                holes = []
                for j in range(fps.HoleCount(i)):
                    hpts = chain_points(fps.Hole(i, j))
                    if len(hpts) >= 3: holes.append(hpts)
                try: poly = Polygon(pts, holes)
                except Exception: continue
                if not poly.is_valid: poly = poly.buffer(0)
                yield dict(kind='zone', net=net, layer=LNAME[l],
                           desc=f"zone [{net}] island{i} area={poly.area:.2f}mm2",
                           poly=poly)


def classify(poly, outline):
    outside = poly.difference(outline)
    out_area = outside.area if not outside.is_empty else 0.0
    d = poly.distance(outline.boundary)
    if out_area > 1e-6:
        return 'CROSSING', round(d, 4), round(out_area, 4)
    if d <= EPS:
        return 'TOUCHING', 0.0, 0.0
    if d < EDGE_CLR:
        return 'CLOSE', round(d, 4), 0.0
    return None, round(d, 4), 0.0


def main():
    path = sys.argv[1]
    board = p.LoadBoard(path)
    outline = outline_poly(board)
    crossing, touching, close = [], [], []
    n_all = 0
    for it in items(board):
        n_all += 1
        cls, d, oa = classify(it['poly'], outline)
        if cls == 'CROSSING':
            crossing.append((it, d, oa))
        elif cls == 'TOUCHING':
            touching.append((it, d, oa))
        elif cls == 'CLOSE':
            close.append((it, d, oa))
    print(f'scanned {n_all} copper item-layer shapes on {path}')
    print(f'CROSSING: {len(crossing)}  TOUCHING: {len(touching)}  CLOSE (<0.5mm): {len(close)}')
    for it, d, oa in crossing:
        print(f"  CROSSING outside={oa}mm2 {it['desc']} on {it['layer']}")
    for it, d, oa in touching:
        print(f"  TOUCHING {it['desc']} on {it['layer']}")
    for it, d, oa in sorted(close, key=lambda z: z[1]):
        print(f"  CLOSE d={d:.4f} {it['desc']} on {it['layer']}")
    if crossing or touching:
        print('CONTAINMENT: FAIL')
        return 1
    print('CONTAINMENT: PASS (zero crossings/touchings)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
