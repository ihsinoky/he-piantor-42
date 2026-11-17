"""Issue #270 case delta: intersect the Rev.9 outline growth (vs Rev.8)
and the full Rev.9 tab region (vs Rev.7), extruded over the board Z band
4.70..5.90, with the #264 audit body set (fitlibF.bodies_at) at both
pitches. Tray hits = pocket relief; any other non-Main body hit is a
finding. Run with the CAD venv python."""
import sys
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-mainoutline/.issue270-runtime')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
import fitlibF as FF
import audit_repair as AR
from build123d import Shape
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.gp import gp_Pnt, gp_Vec
from shapely.geometry import Polygon
from shapely.affinity import translate as shp_translate
import pcbnew as p
from geom2b import outline_of, rev7_case

Q263 = "/home/hatch/workspace/projects/he-piantor-mainoutline/hardware/kicad/qualification/issue-263-implementation"
Q270 = "/home/hatch/workspace/projects/he-piantor-mainoutline/hardware/kicad/qualification/issue-270-main-rev9/main-rev9"

def case(poly_board):
    return shp_translate(poly_board, xoff=-100.0, yoff=-70.0)

rev8 = case(outline_of(p.LoadBoard(f"{Q263}/main-rev8/main.kicad_pcb")))
rev9 = case(outline_of(p.LoadBoard(f"{Q270}/main.kicad_pcb")))
rev7 = rev7_case
growth = rev9.difference(rev8)
tab9 = rev9.difference(rev7)
print("growth area %.3f mm2; tab9 area %.3f mm2; rev8-tab subset check (rev8-rev9 area %.4f)"
      % (growth.area, tab9.area, rev8.difference(rev9).area))

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

for pitch in (17, 16):
    bodies = dict(FF.bodies_at(pitch, -2.65))
    print(f"--- pitch {pitch} ---")
    for label, region in (("growth", growth), ("tab9", tab9)):
        for side_name, clip in (("left", Polygon([(-200, -200), (0, -200), (0, 200), (-200, 200)])),
                                ("right", Polygon([(0, -200), (200, -200), (200, 200), (0, 200)]))):
            reg = region.intersection(clip)
            if reg.area < 1e-9:
                continue
            for solid in extrude(reg):
                for name, body in bodies.items():
                    inter = AR.common_shape(solid, body)
                    v = vol(Shape.cast(inter)) if inter is not None else 0.0
                    if v > 0.005:
                        print(f"{label} {side_name} x {name}: {v:.3f} mm3")
    print(f"(tray bodies present: {[n for n in bodies if 'tray' in n]})")
