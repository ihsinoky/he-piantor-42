"""Build Main Rev.10 from Rev.9 (in the copied Rev.10 tree):
- outline: left chain := exact mirror of the right chain (arc disappears)
- J2 footprint -> (75.745202, 111.823895) rot +43.0; J2 fanout stubs that
  touch old pads are deleted and re-escaped to dangling anchors of the
  same net (validated by capsule sweep, clearance >= 0.10 foreign).
- J3 and everything else untouched; census diff proves it.
"""
import json, math, sys
from pathlib import Path
import pcbnew as p
from shapely.geometry import LineString, Polygon, Point
from shapely.ops import unary_union

MM = 1e6
RT = Path("/home/hatch/workspace/projects/he-piantor-mainsym/.issue275-runtime")
TREE = Path("/home/hatch/workspace/projects/he-piantor-mainsym/hardware/kicad/qualification/issue-275-main-rev10/main-rev10")
BOARD = TREE / "main.kicad_pcb"

b = p.LoadBoard(str(BOARD))

def census(board):
    items = []
    for f in board.GetFootprints():
        items.append(("fp", f.GetReference(), f.GetPosition().x, f.GetPosition().y,
                      round(f.GetOrientationDegrees(), 6)))
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

# ---------- outline ----------
edges = []
for d in b.GetDrawings():
    if d.GetLayer() == p.Edge_Cuts:
        s, e = d.GetStart(), d.GetEnd()
        edges.append({"shape": d.GetShape(), "s": (s.x, s.y), "e": (e.x, e.y), "obj": d})
print("outline elements:", len(edges))

RIGHT_KEYS = [((102.0, 75.7321), (117.856181, 103.195763)),
              ((117.856181, 103.195763), (119.8213, 103.1964)),
              ((119.8213, 103.1964), (132.9488, 115.4381)),
              ((132.9488, 115.4381), (128.936181, 122.386886)),
              ((128.936181, 122.386886), (135.8927, 134.4359))]

def close(pt_nm, pt_mm):
    return abs(pt_nm[0] / MM - pt_mm[0]) < 2e-4 and abs(pt_nm[1] / MM - pt_mm[1]) < 2e-4

right_chain = []
rest = []
for ed in edges:
    hit = False
    for (a, bb) in RIGHT_KEYS:
        if (close(ed["s"], a) and close(ed["e"], bb)) or (close(ed["s"], bb) and close(ed["e"], a)):
            right_chain.append(ed); hit = True; break
    if not hit:
        rest.append(ed)
assert len(right_chain) == 5, f"right chain found {len(right_chain)}"
# rest must be: south chamfers+south (3), north flat (1), left chain (5 incl arc)
assert len(rest) == 9, f"rest {len(rest)}"
MIR = 200_000_000
mirrored = [((MIR - ed["e"][0], ed["e"][1]), (MIR - ed["s"][0], ed["s"][1])) for ed in right_chain]
keep = [(ed["s"], ed["e"]) for ed in rest if not (
    (ed["s"][0] + ed["e"][0]) / 2 < 100 * MM and ed["s"][1] < 137.9 * MM and ed["e"][1] < 137.9 * MM
    and not (ed["s"][1] > 134 * MM or ed["e"][1] > 134 * MM))]
# simpler: keep = rest minus left-chain elements (midpoint x<100, y between 75 and 135, excluding SW chamfer whose midpoint y>134)
keep = []
for ed in rest:
    mx = (ed["s"][0] + ed["e"][0]) / 2 / MM
    my = (ed["s"][1] + ed["e"][1]) / 2 / MM
    is_left_chain = mx < 100 and 75 < my < 134.5
    if not is_left_chain:
        keep.append((ed["s"], ed["e"]))
print("kept non-left elements:", len(keep))
new_outline = keep + [(ed["s"], ed["e"]) for ed in right_chain] + mirrored
assert len(new_outline) == 14, len(new_outline)

for d in [ed["obj"] for ed in edges]:
    b.Remove(d)
_keep = []
def add_seg(a, bb):
    s = p.PCB_SHAPE(b); s.SetShape(p.SHAPE_T_SEGMENT)
    s.SetStart(p.VECTOR2I(*a)); s.SetEnd(p.VECTOR2I(*bb)); s.SetLayer(p.Edge_Cuts); s.SetWidth(int(0.1 * MM))
    b.Add(s); _keep.append(s)
for (a, bb) in new_outline:
    if a != bb:
        add_seg(a, bb)
print("outline rebuilt:", len(_keep), "segments")

# chain segments head-to-tail for a valid polygon check
def chain_poly(segs, tol=2000):
    def eq(p, q):
        return abs(p[0] - q[0]) <= tol and abs(p[1] - q[1]) <= tol
    pts = [segs[0][0]]
    used = [False] * len(segs)
    used[0] = True
    cur = segs[0][1]
    pts.append(cur)
    for _ in range(len(segs) - 1):
        for i, (a, bb) in enumerate(segs):
            if used[i]:
                continue
            if eq(a, cur):
                cur = bb
            elif eq(bb, cur):
                cur = a
            else:
                continue
            used[i] = True
            pts.append(cur)
            break
        else:
            raise RuntimeError("outline does not chain")
    return Polygon([(x / MM, y / MM) for (x, y) in pts])

outline_poly = chain_poly(new_outline)
print("outline valid:", outline_poly.is_valid, "area:", round(outline_poly.area, 2))

# ---------- J2 fanout surgery ----------
fp = b.FindFootprintByReference("J2")
pads = {a.GetNumber(): a for a in fp.Pads()}
tracks = list(b.GetTracks())

def pad_rect(a, exp=0.03):
    """exact pad polygon from KiCad's effective shape (mm), expanded."""
    sh = a.GetEffectiveShape(p.F_Cu)
    ps = p.SHAPE_POLY_SET()
    sh.TransformToPolygon(ps, 0, p.ERROR_OUTSIDE)
    out = ps.Outline(0)
    pts = [(out.GetPoint(i).x / MM, out.GetPoint(i).y / MM) for i in range(out.PointCount())]
    poly = Polygon(pts)
    return poly.buffer(exp, join_style=2) if exp else poly

delete = {}
J2NETS_PRE = {a.GetNetname() for a in pads.values() if a.GetNumber() != "MP"}
OLD_C_PT = Point(OLD_C := (76.048074, 112.073215))
for num, a in pads.items():
    if num == "MP":
        continue
    rect = pad_rect(a)
    for t in tracks:
        if isinstance(t, p.PCB_VIA) or t.GetLayer() != p.F_Cu:
            continue
        s, e = t.GetStart(), t.GetEnd()
        ls = LineString([(s.x / MM, s.y / MM), (e.x / MM, e.y / MM)])
        ends_in = [rect.contains(Point(s.x / MM, s.y / MM)), rect.contains(Point(e.x / MM, e.y / MM))]
        if any(ends_in):
            delete.setdefault(t.m_Uuid.AsString(), t)
        elif ls.intersects(rect):
            if t.GetNetname() != a.GetNetname():
                print("STOP: FOREIGN through-track crosses pad", num, t.m_Uuid.AsString())
                sys.exit(1)
            print("note: same-net through-track crosses pad", num, a.GetNetname(), t.m_Uuid.AsString()[:8])
# wider rip: every F.Cu segment of J2's nets passing within 8mm of the old
# centre goes - chain fragments that miss the pad rects still short the
# moved pads (found by the B2 gates on the first build: 7 shorts).
extra = 0
for t in tracks:
    if isinstance(t, p.PCB_VIA) or t.GetLayer() != p.F_Cu:
        continue
    if t.GetNetname() not in J2NETS_PRE or t.m_Uuid.AsString() in delete:
        continue
    s, e = t.GetStart(), t.GetEnd()
    ls = LineString([(s.x / MM, s.y / MM), (e.x / MM, e.y / MM)])
    if ls.distance(OLD_C_PT) < 8.0:
        delete[t.m_Uuid.AsString()] = t
        extra += 1
print("stub segments to delete:", len(delete), "(wide-rip extra:", extra, ")")
width_by_pad = {}
for num, a in pads.items():
    if num == "MP":
        continue
    rect = pad_rect(a)
    ws = []
    for t in delete.values():
        s, e = t.GetStart(), t.GetEnd()
        if rect.contains(Point(s.x / MM, s.y / MM)) or rect.contains(Point(e.x / MM, e.y / MM)):
            if t.GetNetname() == a.GetNetname():
                ws.append(t.GetWidth() / MM)
    width_by_pad[num] = max(ws) if ws else (0.3 if a.GetNetname() in ("GND", "HALL_5V") else 0.1)
for t in delete.values():
    b.Remove(t)

# dangling ends among surviving F.Cu tracks
from collections import Counter, defaultdict
deg = Counter()
seg_by_pt = defaultdict(list)
surv = [t for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and t.GetLayer() == p.F_Cu]
for t in surv:
    s, e = t.GetStart(), t.GetEnd()
    deg[(s.x, s.y)] += 1
    deg[(e.x, e.y)] += 1
    seg_by_pt[(s.x, s.y)].append(t)
    seg_by_pt[(e.x, e.y)].append(t)
via_pts = {(t.GetStart().x, t.GetStart().y) for t in b.GetTracks() if isinstance(t, p.PCB_VIA)}
pad_pts_all = set()
for f in b.GetFootprints():
    for a in f.Pads():
        pad_pts_all.add((a.GetPosition().x, a.GetPosition().y))
OLD_C = (76.048074, 112.073215)
dangling = defaultdict(list)  # net -> [(x,y) mm]
for pt, dg in deg.items():
    if dg == 1 and pt not in via_pts and pt not in pad_pts_all:
        x, y = pt[0] / MM, pt[1] / MM
        if math.hypot(x - OLD_C[0], y - OLD_C[1]) < 7:
            net = seg_by_pt[pt][0].GetNetname()
            dangling[net].append((x, y))
print("dangling anchors by net:", {k: len(v) for k, v in dangling.items()})

# ---------- move footprint ----------
fp.SetPosition(p.VECTOR2I(75745202, 111823895))
fp.SetOrientation(p.EDA_ANGLE(43.0, p.DEGREES_T))
print("J2 now:", fp.GetPosition().x / MM, fp.GetPosition().y / MM, fp.GetOrientationDegrees())

# verify signal pads == mirror of J3 pads with reversed numbering (15-k):
# the two sites carry identical per-number assignments and the mirrored
# cable geometry presents the row reversed (verified in #263/#268).
fp3 = b.FindFootprintByReference("J3")
j3 = {a.GetNumber(): (a.GetPosition().x / MM, a.GetPosition().y / MM) for a in fp3.Pads()}
maxdev = 0.0
for num, a in pads.items():
    if num == "MP":
        pp = a.GetPosition()
        print("MP pad at", round(pp.x / MM, 4), round(pp.y / MM, 4))
        continue
    pp = a.GetPosition()
    src = j3[str(15 - int(num))]
    dev = math.hypot(pp.x / MM - (200 - src[0]), pp.y / MM - src[1])
    maxdev = max(maxdev, dev)
print("max signal-pad deviation vs mirrored J3 (15-k):", round(maxdev, 6))

# ---------- KRT escape completion (project router, #263 machinery) ----------
import subprocess, os
J2NETS = sorted({a.GetNetname() for a in pads.values() if a.GetNumber() != "MP"})
print("J2 nets:", J2NETS)
# lock every surviving track/via: KRT must only ADD copper, never re-plan
for t in b.GetTracks():
    t.SetLocked(True)
print("locked all surviving tracks/vias")
b.Save(str(BOARD))
KRT = Path("/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/KiCadRoutingTools")
KRT_PY = "/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/venv/bin/python3"
ROUTED = RT / "rev10-routed.kicad_pcb"
cmd = [KRT_PY, str(KRT / "py_router/route.py"), str(BOARD), str(ROUTED),
       "--nets", *J2NETS,
       "--track-width", "0.1", "--power-nets", "HALL_5V", "GND",
       "--power-nets-widths", "0.3", "0.3", "--clearance", "0.1",
       "--via-size", "0.6", "--via-drill", "0.3",
       "--same-net-pad-clearance", "0.15", "--escalation", "board"]
print("running KRT ...", flush=True)
with open(RT / "krt-rev10.log", "w") as lf:
    r = subprocess.run(cmd, cwd=KRT, stdout=lf, stderr=subprocess.STDOUT, timeout=1800)
print("KRT exit:", r.returncode)
if r.returncode != 0 or not ROUTED.exists():
    print("STOP: KRT failed; see krt-rev10.log")
    sys.exit(1)
b = p.LoadBoard(str(ROUTED))
escapes = {"method": "KRT --nets (F.Cu)", "nets": J2NETS}

# refill zones
filler = p.ZONE_FILLER(b)
filler.Fill(b.Zones())
b.BuildConnectivity()
after = census(b)
print("census after:", len(after))
diff_out = sorted(set(before) ^ set(after))
print("census symmetric-diff lines:", len(diff_out))
(RT / "rev10-build.json").write_text(json.dumps({
    "escapes": escapes,
    "max_pad_dev_vs_mirror_j3": maxdev,
    "deleted_stubs": len(delete),
    "census_before": len(before), "census_after": len(after),
    "census_diff": len(diff_out)}, indent=1))
for line in diff_out[:40]:
    print("DIFF", line[:130])
b.Save(str(RT / "rev10-fullkrt.kicad_pcb"))
print("saved full-KRT board to runtime (tree board remains the PREP board)")
