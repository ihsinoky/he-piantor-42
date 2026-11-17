#!/usr/bin/env python3
"""Issue #273 case delta: the Wing Rev.6 outline GREW vs both the 2d
board and Rev.5 (the straight dive line fills Rev.5's mouth scallops
back in). Extrude the added regions (case frame) over the board Z
band 4.70..5.90 and intersect with the #264 audit body set
(fitlibF.bodies_at, s=-2.65) at both pitches - the case-delta-2d
method. Any hit on a non-Wing body (tray, cable, Main, ...) is a
finding; hits on the audited Wing solid itself are expected wherever
the KiCad outline differs from the round18 audit solid and are
reported separately. Run with kpy.sh (pcbnew + build123d env)."""
import sys
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-mainoutline/.issue270-runtime')
import fitlibF as FF
import audit_repair as AR
from build123d import Shape
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.gp import gp_Pnt, gp_Vec
from shapely.geometry import Polygon
from shapely.affinity import rotate as shp_rotate, translate as shp_translate
import pcbnew as p
from notchain import wing_xf_factory

MM = 1e6
W = "/home/hatch/workspace/projects/he-piantor-wingnotch"
Q263 = f"{W}/hardware/kicad/qualification/issue-263-implementation"
Q270W = f"{W}/hardware/kicad/qualification/issue-270-wing-rev6"
OLD2D = f"{W}/.issue273-runtime/old2d"


def outline_of(board):
    ps = p.SHAPE_POLY_SET(); board.GetBoardPolygonOutlines(ps)
    ch = ps.Outline(0)
    return Polygon([(ch.CPoint(j).x / MM, ch.CPoint(j).y / MM)
                    for j in range(ch.PointCount())])


def case_of(board, side):
    fwd, inv, jw = wing_xf_factory(board, side)
    ang = 30.5 if side == "left" else -30.5
    env = (-27.0, -37.5) if side == "left" else (27.0, -37.5)
    q = shp_translate(outline_of(board), xoff=-jw[0], yoff=-jw[1])
    q = shp_rotate(q, ang, origin=(0, 0))
    return shp_translate(q, xoff=env[0], yoff=env[1])


def extrude(poly, z0=4.70, h=1.2):
    solids = []
    parts = list(poly.geoms) if poly.geom_type == "MultiPolygon" else [poly]
    for part in parts:
        if part.area < 1e-9:
            continue
        mp = BRepBuilderAPI_MakePolygon()
        for x, y in part.exterior.coords[:-1]:
            mp.Add(gp_Pnt(x, y, z0))
        mp.Close()
        face = BRepBuilderAPI_MakeFace(mp.Wire(), True).Face()
        solids.append(Shape.cast(BRepPrimAPI_MakePrism(face, gp_Vec(0, 0, h)).Shape()))
    return solids


def vol(shape):
    try:
        return float(shape.volume)
    except Exception:
        return sum(float(s.volume) for s in shape.solids())


SUMMARY = {}
for variant in ("17mm-left", "17mm-right", "16mm-left", "16mm-right"):
    pitch_s, side = variant.split("-")
    pitch = int(pitch_s[:2])
    new = case_of(p.LoadBoard(f"{Q270W}/wing-rev6-{variant}/main.kicad_pcb"), side)
    old2d = case_of(p.LoadBoard(f"{OLD2D}/wing-rev6-{variant}.kicad_pcb"), side)
    rev5 = case_of(p.LoadBoard(f"{Q263}/wing-rev5-{variant}/main.kicad_pcb"), side)
    bodies = dict(FF.bodies_at(pitch, -2.65))
    own = f"wing_{side}"
    print(f"--- {variant} (pitch {pitch}) ---")
    for label, region in (("added_vs_2d", new.difference(old2d)),
                          ("added_vs_rev5", new.difference(rev5))):
        print(f"  {label}: {region.area:.3f} mm2")
        hits = []
        for solid in extrude(region):
            for name, body in bodies.items():
                inter = AR.common_shape(solid, body)
                v = vol(Shape.cast(inter)) if inter is not None else 0.0
                if v > 0.005:
                    hits.append((name, v))
        for name, v in sorted(hits, key=lambda t: -t[1]):
            tag = "OWN-WING" if name == own else "FINDING"
            print(f"    x {name}: {v:.3f} mm3 [{tag}]")
        if not hits:
            print("    no body hits")
        SUMMARY[f"{variant}/{label}"] = {"area": region.area,
                                        "hits": sorted(([n, round(v, 3)] for n, v in hits), key=lambda t: -t[1])}
import json as _json
from pathlib import Path
Path("/home/hatch/workspace/projects/he-piantor-wingnotch/.issue273-runtime/case-delta-2e.json").write_text(_json.dumps(SUMMARY, indent=1))
print("DONE")
