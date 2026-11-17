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
Q270W = f"{W}/hardware/kicad/qualification/issue-270-wing-rev6"
OLD2D = f"{W}/.issue273-runtime/old2d"

def outline_of(board):
    ps = p.SHAPE_POLY_SET(); board.GetBoardPolygonOutlines(ps)
    ch = ps.Outline(0)
    return Polygon([(ch.CPoint(j).x / MM, ch.CPoint(j).y / MM) for j in range(ch.PointCount())])

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
        if part.area < 1e-9: continue
        mp = BRepBuilderAPI_MakePolygon()
        for x, y in part.exterior.coords[:-1]: mp.Add(gp_Pnt(x, y, z0))
        mp.Close()
        face = BRepBuilderAPI_MakeFace(mp.Wire(), True).Face()
        solids.append(Shape.cast(BRepPrimAPI_MakePrism(face, gp_Vec(0, 0, h)).Shape()))
    return solids

def vol(s):
    try: return float(s.volume)
    except Exception: return sum(float(x.volume) for x in s.solids())

def bb2(sh):
    b = sh.bounding_box()
    return (round(b.min.X,2), round(b.min.Y,2), round(b.max.X,2), round(b.max.Y,2))

bodies = dict(FF.bodies_at(17, -2.65))
for variant, side in (("17mm-right","right"), ("17mm-left","left")):
    new = case_of(p.LoadBoard(f"{Q270W}/wing-rev6-{variant}/main.kicad_pcb"), side)
    old = case_of(p.LoadBoard(f"{OLD2D}/wing-rev6-{variant}.kicad_pcb"), side)
    region = new.difference(old)
    print(f"== {variant}: added area {region.area:.3f}, new outline bounds {tuple(round(v,1) for v in new.bounds)}")
    parts = list(region.geoms) if region.geom_type == "MultiPolygon" else [region]
    for i, part in enumerate(parts):
        print(f"  part{i} area {part.area:.3f} bounds {tuple(round(v,2) for v in part.bounds)}")
        for solid in extrude(part):
            for name in ('tray-left','tray-right', f'wing_{side}'):
                inter = AR.common_shape(solid, bodies[name])
                v = vol(Shape.cast(inter)) if inter is not None else 0.0
                if v > 0.005:
                    print(f"    x {name}: {v:.3f} bbox {bb2(Shape.cast(inter))}")
