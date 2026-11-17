"""Verify Main Rev.9: outline vs spec polygon, pad-corner clearance
(stage-1 BBox yardstick), edge-to-copper clearance, and copper
invariance vs Rev.8 (everything except Edge.Cuts identical)."""
import hashlib, json, sys
from pathlib import Path
import pcbnew as p
from shapely.geometry import Point, LineString
from shapely.ops import unary_union
sys.path.insert(0, "/home/hatch/workspace/projects/he-piantor-mainoutline/.issue270-runtime")
from geom2b import outline_of, polys_of, main_new_board, copper_items

MM = 1e6
Q263 = Path("/home/hatch/workspace/projects/he-piantor-mainoutline/hardware/kicad/qualification/issue-263-implementation")
NEW = Path("/home/hatch/workspace/projects/he-piantor-mainoutline/hardware/kicad/qualification/issue-270-main-rev9")

b_old = p.LoadBoard(str(Q263 / "main-rev8/main.kicad_pcb"))
b_new = p.LoadBoard(str(NEW / "main.kicad_pcb"))

out_new = outline_of(b_new)
print("outline area: %.3f (spec %.3f)  symdiff: %.5f mm2  valid: %s" % (
    out_new.area, main_new_board.area, out_new.symmetric_difference(main_new_board).area, out_new.is_valid))

# pad-corner clearance (BBox corners, stage-1 yardstick) — ZIF pads (spec metric)
def pad_clearance(b, out, refs=None):
    worst, worst_id, uncovered = 1e9, None, 0
    for f in b.GetFootprints():
        if refs and f.GetReference() not in refs:
            continue
        for a in f.Pads():
            bb = a.GetBoundingBox()
            for cx, cy in ((bb.GetLeft(), bb.GetTop()), (bb.GetRight(), bb.GetTop()),
                           (bb.GetLeft(), bb.GetBottom()), (bb.GetRight(), bb.GetBottom())):
                pt = Point(cx / MM, cy / MM)
                if not out.covers(pt):
                    uncovered += 1
                d = out.exterior.distance(pt)
                if d < worst:
                    worst, worst_id = d, f.GetReference() + "." + a.GetNumber()
    return worst, worst_id, uncovered

out_old = outline_of(b_old)
for tag, b, out in (("Rev.9", b_new, out_new), ("Rev.8", b_old, out_old)):
    w, wid, unc = pad_clearance(b, out, refs=("J2", "J3"))
    print("%s ZIF pad-corner clearance: %.4f at %s; uncovered: %d" % (tag, w, wid, unc))
    w, wid, unc = pad_clearance(b, out)
    print("%s ALL-pads worst: %.4f at %s; uncovered: %d" % (tag, w, wid, unc))

# edge-to-copper clearance (tracks/vias/pads/fills, true shapes), both boards
for tag, b, out in (("Rev.9", b_new, out_new), ("Rev.8", b_old, out_old)):
    items = copper_items(b)
    mind, mink = 1e9, None
    for kind, geom in items:
        if kind == "zonepoly":
            continue
        d = out.exterior.distance(geom)
        if d < mind:
            mind, mink = d, kind
    print("%s min edge-to-copper (whole board): %.4f (%s)" % (tag, mind, mink))

# copper invariance: signatures of everything except Edge.Cuts drawings
def sig(b):
    s = []
    for f in b.GetFootprints():
        s.append(("fp", f.GetReference(), f.GetValue(), str(f.GetPosition()), f.GetOrientationDegrees(),
                  tuple(sorted((a.GetNumber(), a.GetNetname(), str(a.GetPosition()), str(a.GetSize())) for a in f.Pads()))))
    for t in b.GetTracks():
        s.append(("tr", type(t).__name__, t.GetNetname(), str(t.GetStart()), str(t.GetEnd()), t.GetWidth(), tuple(t.GetLayerSet().Seq())))
    for z in b.Zones():
        h = hashlib.sha256()
        for l in z.GetLayerSet().Seq():
            ps = z.GetFilledPolysList(l)
            for i in range(ps.OutlineCount()):
                o = ps.Outline(i)
                h.update(bytes(str([(o.CPoint(j).x, o.CPoint(j).y) for j in range(o.PointCount())]), "utf8"))
        s.append(("zone", z.GetZoneName(), h.hexdigest()))
    for d in b.GetDrawings():
        if d.GetLayer() != p.Edge_Cuts:
            s.append(("dw", str(d.GetLayer()), str(d.GetStart()), str(d.GetEnd())))
    return sorted(str(x) for x in s)

so, sn = sig(b_old), sig(b_new)
print("copper invariance: old items %d, new items %d, identical: %s" % (len(so), len(sn), so == sn))
if so != sn:
    for a, bb in zip(so, sn):
        if a != bb:
            print("first diff:\n old:", a[:200], "\n new:", bb[:200]); break
