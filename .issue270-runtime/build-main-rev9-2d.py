"""Build Main Rev.9 stage 2d IN PLACE: replace the two tab zones'
Edge.Cuts in the current Rev.9 board with the Stage 2c connector-
aligned fronts (+ R0.50 fillet at the J2 diving corner, stage2d.json).
Outline-only: everything else must stay identical - verified by an
item census (all non-Edge.Cuts items) before/after and by comparing
the rebuilt outline against the design polygon (stage2d-polys.json).
The fillet tangent point Tw sits 0.0017 mm from the existing base1
vertex W0; the board arc starts exactly at W0 (snap disclosed)."""
import json, math, sys
from pathlib import Path
import pcbnew as p
from shapely.geometry import Polygon
from shapely.ops import unary_union

MM = 1e6
RT = Path("/home/hatch/workspace/projects/he-piantor-mainoutline/.issue270-runtime")
TREE = Path("/home/hatch/workspace/projects/he-piantor-mainoutline/hardware/kicad/qualification/issue-270-main-rev9/main-rev9")
sys.path.insert(0, str(RT))
from geom2b import outline_of

D = json.loads((RT / "stage2d.json").read_text())
F = D["fillet"]
CORN = D["corners_case"]  # case frame PL/PR per site

def V(x, y):
    return p.VECTOR2I(round(x * MM), round(y * MM))

def boardpt(case_xy):
    return (case_xy[0] + 100.0, case_xy[1] + 70.0)

b = p.LoadBoard(str(TREE / "main.kicad_pcb"))

# ---- census of everything except Edge.Cuts drawings ----
def census(board):
    items = []
    for f in board.GetFootprints():
        items.append(("fp", f.GetReference(), f.GetPosition().x, f.GetPosition().y,
                      round(f.GetOrientationDegrees(), 6), f.GetValue()))
        for a in f.Pads():
            items.append(("pad", f.GetReference(), a.GetNumber(), a.GetPosition().x, a.GetPosition().y))
    for t in board.GetTracks():
        items.append(("via" if isinstance(t, p.PCB_VIA) else "trk",
                      t.m_Uuid.AsString(), t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y,
                      t.GetNetname(), t.GetLayer()))
    for z in board.Zones():
        items.append(("zone", z.m_Uuid.AsString(), z.GetZoneName(), z.GetNetname()))
    for d in board.GetDrawings():
        if d.GetLayer() != p.Edge_Cuts:
            items.append(("drw", d.m_Uuid.AsString(), d.GetLayer(), d.GetShape()))
    return sorted(str(i) for i in items)

before = census(b)
print("census before:", len(before))

edges = [d for d in b.GetDrawings() if d.GetLayer() == p.Edge_Cuts]
def ekey(d):
    return (tuple(round(v / MM, 4) for v in (d.GetStart().x, d.GetStart().y)),
            tuple(round(v / MM, 4) for v in (d.GetEnd().x, d.GetEnd().y)))
segmap = {}
for d in edges:
    k = ekey(d)
    segmap.setdefault(k, d); segmap.setdefault((k[1], k[0]), d)

def find_near(a, bb, tol=0.01):
    for (p1, p2), d in segmap.items():
        if math.dist(p1, a) < tol and math.dist(p2, bb) < tol:
            return d
    return None

# Rev.9 tab corners (board frame; from the 2b build / TAB_BOARD record)
TAB9 = {
    "J2": dict(base1=(82.0535, 103.3522), front1=(76.5824, 103.3518), front2=(68.2378, 117.805), base2=(70.9735, 122.5433)),
    "J3": dict(base1=(117.8562, 103.1958), front1=(123.3272, 103.1958), front2=(131.6717, 117.6489), base2=(128.9362, 122.3869)),
}
removed = []
def remove(a, bb, why):
    d = find_near(a, bb)
    assert d is not None, f"segment not found {a}->{bb} ({why})"
    removed.append(why); b.Remove(d)

def add_seg(a, bb):
    s = p.PCB_SHAPE(b)
    s.SetShape(p.SHAPE_T_SEGMENT)
    s.SetStart(V(*a)); s.SetEnd(V(*bb))
    s.SetLayer(p.Edge_Cuts); s.SetWidth(int(0.1 * MM))
    b.Add(s)

def add_arc(a, mid, bb):
    s = p.PCB_SHAPE(b)
    s.SetShape(p.SHAPE_T_ARC)
    s.SetArcGeometry(V(*a), V(*mid), V(*bb))
    s.SetLayer(p.Edge_Cuts); s.SetWidth(int(0.1 * MM))
    b.Add(s)

# ---- J2: base1 -> arc(W0->Tf) -> Tf -> PR -> base2 ----
t = TAB9["J2"]
remove(t["base1"], t["front1"], "J2 wall dive")
remove(t["front1"], t["front2"], "J2 front")
remove(t["front2"], t["base2"], "J2 wall rise")
W0 = (t["base1"][0], t["base1"][1])           # existing vertex, exact
Tf = tuple(F["Tf_board"]); PR = boardpt(CORN["J2"]["PR"])
add_arc(W0, tuple(F["arc_mid_board"]), Tf)
add_seg(Tf, PR)
add_seg(PR, t["base2"])
print("J2 chain: arc", W0, "->", Tf, " seg ->", PR, " seg ->", t["base2"])

# ---- J3: base1 -> PR -> PL -> base2 ----
t = TAB9["J3"]
remove(t["base1"], t["front1"], "J3 wall")
remove(t["front1"], t["front2"], "J3 front")
remove(t["front2"], t["base2"], "J3 wall")
PR3 = boardpt(CORN["J3"]["PR"]); PL3 = boardpt(CORN["J3"]["PL"])
add_seg(t["base1"], PR3)
add_seg(PR3, PL3)
add_seg(PL3, t["base2"])
print("J3 chain:", t["base1"], "->", PR3, "->", PL3, "->", t["base2"])
print("removed:", removed)

p.SaveBoard(str(TREE / "main.kicad_pcb"), b)

# ---- verify ----
b2 = p.LoadBoard(str(TREE / "main.kicad_pcb"))
after = census(b2)
assert before == after, "NON-OUTLINE CENSUS CHANGED"
print("census after:", len(after), "- identical (non-Edge.Cuts items unchanged)")
new_poly = outline_of(b2)
design = Polygon(json.loads((RT / "stage2d-polys.json").read_text())["main_final"])
design_board = Polygon([(x + 100.0, y + 70.0) for x, y in design.exterior.coords])
sd = new_poly.symmetric_difference(design_board)
print(f"outline vs design polygon: board area {new_poly.area:.3f}, design {design_board.area:.3f}, "
      f"symdiff {sd.area:.5f} mm2")
assert sd.area < 0.05, "outline deviates from design polygon"
print("Main Rev.9 stage 2d board saved OK")
