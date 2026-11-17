"""Build Main Rev.9: Rev.8 board with ONLY the two tab zones' Edge.Cuts
replaced by the approved Stage 2a trapezoid spec (design-doc corner
table: front half 8.3445 @ d=4.738, base half 11.0795 @ d=0, walls 60deg).
J2 front corners coincide with Rev.8's (snapped to existing vertices);
J3 front edge moves ~0.1 mm (depth 4.721 -> 4.738, centred per spec)."""
import json, math, shutil, sys
from pathlib import Path
import pcbnew as p

MM = 1e6
RT = Path("/home/hatch/workspace/projects/he-piantor-mainoutline/.issue270-runtime")
Q263 = Path("/home/hatch/workspace/projects/he-piantor-mainoutline/hardware/kicad/qualification/issue-263-implementation")
OUT = Path("/home/hatch/workspace/projects/he-piantor-mainoutline/hardware/kicad/qualification/issue-270-main-rev9")
sys.path.insert(0, str(RT))
from geom2b import td_to_case, sites, TC, FRONT_HALF, BASE_HALF, DEPTH

def V(x, y):
    return p.VECTOR2I(round(x * MM), round(y * MM))

def board_pt(site, t, d):
    c = td_to_case(sites[site], t, d)
    return (c[0] + 100.0, c[1] + 70.0)

# trapezoid corners per site, ordered along the outline traversal
# (from the site's apex-side edge vertex): base_near, front_near, front_far, base_far.
# NOTE: the J3 site frame's t axis runs opposite to the traversal, so
# ordering must come from geometry, not from t.
APEX = {"J2": (98.0, 75.7321), "J3": (102.0, 75.7321)}
CORN = {}
for s in ("J2", "J3"):
    tc = TC[s]
    bases = sorted((board_pt(s, tc - BASE_HALF, 0.0), board_pt(s, tc + BASE_HALF, 0.0)),
                   key=lambda pt: math.dist(pt, APEX[s]))
    fronts = sorted((board_pt(s, tc - FRONT_HALF, DEPTH), board_pt(s, tc + FRONT_HALF, DEPTH)),
                    key=lambda pt: math.dist(pt, APEX[s]))
    CORN[s] = {"base1": bases[0], "base2": bases[1], "front1": fronts[0], "front2": fronts[1]}
    print(s, {k: tuple(round(v, 4) for v in pt) for k, pt in CORN[s].items()})

src = Q263 / "main-rev8"
b = p.LoadBoard(str(src / "main.kicad_pcb"))
print("title rev:", b.GetTitleBlock().GetRevision(), "| title:", b.GetTitleBlock().GetTitle())

edges = [d for d in b.GetDrawings() if d.GetLayer() == p.Edge_Cuts]
def key(d):
    return (tuple(round(v / MM, 4) for v in (d.GetStart().x, d.GetStart().y)),
            tuple(round(v / MM, 4) for v in (d.GetEnd().x, d.GetEnd().y)))
segmap = {}
for d in edges:
    segmap.setdefault(key(d), d)
    segmap.setdefault((key(d)[1], key(d)[0]), d)

def find(a, bb):
    ka = (tuple(round(v, 4) for v in a), tuple(round(v, 4) for v in bb))
    return segmap.get(ka)

# Rev.8 tab-zone vertices (from the board dump)
J2 = dict(P1=(80.6859, 105.7209), A=(76.5824, 103.3518), B=(68.2378, 117.805), P2=(72.3413, 120.1742),
          apex=(98.0, 75.7321), sw=(64.1073, 134.4359))
J3 = dict(apex=(102.0, 75.7321), P1=(119.275, 105.6533), A=(123.3638, 103.2927), B=(131.6069, 117.5701),
          P2=(127.5181, 119.9307), se=(135.8927, 134.4359))

removed, added = [], []
def remove(a, bb, why):
    d = find(a, bb)
    assert d is not None, f"segment not found {a}->{bb} ({why})"
    removed.append((a, bb, why)); b.Remove(d)

def add(a, bb):
    s = p.PCB_SHAPE(b)
    s.SetShape(p.SHAPE_T_SEGMENT)
    s.SetStart(V(*a)); s.SetEnd(V(*bb))
    s.SetLayer(p.Edge_Cuts); s.SetWidth(int(0.1 * MM))
    b.Add(s); added.append((a, bb))

# ---- J2 (west edge, traversal apex -> SW corner) ----
c = CORN["J2"]
snapA, snapB = J2["A"], J2["B"]  # front corners identical to Rev.8 within 0.5 um: snap
for pt, ref in ((c["front1"], snapA), (c["front2"], snapB)):
    assert math.dist(pt, ref) < 0.002, (pt, ref)
remove(J2["apex"], J2["P1"], "J2 edge trim")
remove(J2["P1"], J2["A"], "J2 wall1")
remove(J2["B"], J2["P2"], "J2 wall2")
remove(J2["P2"], J2["sw"], "J2 edge trim")
# front edge segment A->B kept untouched
add(J2["apex"], c["base1"]); add(c["base1"], snapA)
add(snapB, c["base2"]); add(c["base2"], J2["sw"])

# ---- J3 (east edge, traversal apex -> SE corner) ----
c = CORN["J3"]
remove(J3["P1"], J3["apex"], "J3 edge trim")
remove(J3["P1"], J3["A"], "J3 wall1")
remove(J3["A"], J3["B"], "J3 front")
remove(J3["B"], J3["P2"], "J3 wall2")
remove(J3["se"], J3["P2"], "J3 edge trim")
add(J3["apex"], c["base1"]); add(c["base1"], c["front1"]); add(c["front1"], c["front2"])
add(c["front2"], c["base2"]); add(c["base2"], J3["se"])

print("removed:", len(removed), "added:", len(added))
OUT.mkdir(parents=True, exist_ok=True)
p.SaveBoard(str(OUT / "main.kicad_pcb"), b)
for f in ("main.kicad_pro", "main.kicad_prl", "input.kicad_pro", "main.kicad_sch",
          "fp-lib-table", "sym-lib-table", "review.kicad_sym"):
    if (src / f).exists():
        shutil.copyfile(src / f, OUT / f)
print("saved", OUT / "main.kicad_pcb")
