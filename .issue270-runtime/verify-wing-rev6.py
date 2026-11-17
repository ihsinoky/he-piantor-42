"""Verify one Wing Rev.6 variant against its Rev.5 source:
outline vs the exact buffer construction (case frame), seam vs the
implemented Rev.9 (tab zone), copper invariance excluding fills, and
the fill delta confinement (recomputed from the saved files).
Usage: verify-wing-rev6.py <variant>"""
import hashlib, math, sys
from pathlib import Path
import pcbnew as p
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from shapely.affinity import rotate as shp_rotate, translate as shp_translate

MM = 1e6
RT = Path("/home/hatch/workspace/projects/he-piantor-mainoutline/.issue270-runtime")
Q263 = Path("/home/hatch/workspace/projects/he-piantor-mainoutline/hardware/kicad/qualification/issue-263-implementation")
Q270M = Path("/home/hatch/workspace/projects/he-piantor-mainoutline/hardware/kicad/qualification/issue-270-main-rev9")
Q270W = Path("/home/hatch/workspace/projects/he-piantor-mainoutline/hardware/kicad/qualification/issue-270-wing-rev6")
sys.path.insert(0, str(RT))
from geom2b import outline_of, polys_of
from notchain import wing_xf_factory

variant = sys.argv[1]
pitch, side = variant.split("-")
b_old = p.LoadBoard(str(Q263 / f"wing-rev5-{variant}" / "main.kicad_pcb"))
b_new = p.LoadBoard(str(Q270W / f"wing-rev6-{variant}" / "main.kicad_pcb"))
fwd, inv, jw = wing_xf_factory(b_old, side)

def poly_to_case(poly_board):
    q = shp_translate(poly_board, xoff=-jw[0], yoff=-jw[1])
    deg = 30.5 if side == "left" else -30.5
    q = shp_rotate(q, deg, origin=(0, 0))
    env = (-27.0, -37.5) if side == "left" else (27.0, -37.5)
    return shp_translate(q, xoff=env[0], yoff=env[1])

old_case = poly_to_case(outline_of(b_old))
new_case = poly_to_case(outline_of(b_new))
mb = p.LoadBoard(str(Q270M / "main-rev9" / "main.kicad_pcb"))
main9_case = shp_translate(outline_of(mb), xoff=-100.0, yoff=-70.0)
expect_case = old_case.difference(main9_case.buffer(0.55, resolution=64))
print(f"{variant}: outline area new {new_case.area:.3f} expect {expect_case.area:.3f}; "
      f"symdiff {new_case.symmetric_difference(expect_case).area:.4f} mm2; valid {new_case.is_valid}")

# seam in the tab zone: wing boundary points within 14 mm of the tab
site = "J2" if side == "left" else "J3"
TAB = {"J2": (-23.85, 42.95), "J3": (23.85, 42.8)}[site]
zone = Point(TAB).buffer(14)
pts = [Point(c) for c in new_case.exterior.coords if zone.covers(Point(c))]
dists = [pt.distance(main9_case) for pt in pts]
print("seam (tab zone): min %.4f  overlap area %.5f" % (min(dists), new_case.intersection(main9_case).area))

# copper invariance excluding Edge.Cuts and zone fills
def sig(b, with_fills=False):
    s = []
    for f in b.GetFootprints():
        s.append(("fp", f.GetReference(), f.GetValue(), str(f.GetPosition()), f.GetOrientationDegrees(),
                  tuple(sorted((a.GetNumber(), a.GetNetname(), str(a.GetPosition()), str(a.GetSize())) for a in f.Pads()))))
    for t in b.GetTracks():
        s.append(("tr", type(t).__name__, t.GetNetname(), str(t.GetStart()), str(t.GetEnd()), t.GetWidth(), tuple(t.GetLayerSet().Seq())))
    for z in b.Zones():
        s.append(("zone", z.GetZoneName(), z.GetNetname(),
                  str([(pt.x, pt.y) for pt in z.Outline().AllPoints()]) if hasattr(z.Outline(), "AllPoints") else ""))
    for d in b.GetDrawings():
        if d.GetLayer() != p.Edge_Cuts:
            s.append(("dw", str(d.GetLayer()), str(d.GetStart()), str(d.GetEnd())))
    return sorted(str(x) for x in s)
so, sn = sig(b_old), sig(b_new)
print("copper invariance (excl. fills):", so == sn, f"({len(so)} items)")

# fill delta confinement, recomputed
removed_board = outline_of(b_old).difference(outline_of(b_new))
tot = {}
for z_old, z_new in zip(b_old.Zones(), b_new.Zones()):
    for l in z_old.GetLayerSet().Seq():
        fo = polys_of(z_old.GetFilledPolysList(l))
        fn = polys_of(z_new.GetFilledPolysList(l))
        delta = fo.symmetric_difference(fn)
        outside = delta.difference(removed_board.buffer(0.75))
        if delta.area > 1e-4:
            print(f"fill {z_old.GetNetname()} L{l}: delta {delta.area:.3f}, outside band {outside.area:.4f}")
print("done", variant)
