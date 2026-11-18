"""Fresh-process census diff Rev.9 vs Rev.10 + J3 bit-identity + outline mirror check."""
import json, math, ast
from pathlib import Path
import pcbnew as p

MM = 1e6
RT = Path("/home/hatch/workspace/projects/he-piantor-mainsym/.issue275-runtime")
REV9 = Path("/home/hatch/workspace/projects/he-piantor-mainsym/hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb")
REV10 = Path("/home/hatch/workspace/projects/he-piantor-mainsym/hardware/kicad/qualification/issue-275-main-rev10/main-rev10/main.kicad_pcb")
J2C = (76.048074, 112.073215)

def census(board):
    items = []
    for f in board.GetFootprints():
        items.append(("fp", f.GetReference(), f.GetPosition().x, f.GetPosition().y, round(f.GetOrientationDegrees(), 6)))
        for a in f.Pads():
            items.append(("pad", f.GetReference(), a.GetNumber(), a.GetPosition().x, a.GetPosition().y))
    for t in board.GetTracks():
        items.append(("via" if isinstance(t, p.PCB_VIA) else "trk", t.m_Uuid.AsString(),
                      t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y, t.GetNetname(), t.GetLayer()))
    for z in board.Zones():
        items.append(("zone", z.m_Uuid.AsString(), z.GetZoneName(), z.GetNetname()))
    for d in board.GetDrawings():
        if d.GetLayer() != p.Edge_Cuts:
            items.append(("drw", d.m_Uuid.AsString(), d.GetLayer(), d.GetShape()))
    return sorted(str(i) for i in items)

b9 = p.LoadBoard(str(REV9))
c9 = census(b9)
j3_9 = [i for i in c9 if "'J3'" in i]
del b9
b10 = p.LoadBoard(str(REV10))
c10 = census(b10)
j3_10 = [i for i in c10 if "'J3'" in i]
print("census:", len(c9), "->", len(c10), "| diff:", len(set(c9) ^ set(c10)))
print("J3 items identical:", j3_9 == j3_10, f"({len(j3_9)} items)")
diff = sorted(set(c9) ^ set(c10))
far = []
for line in diff:
    if line.startswith("('trk'") or line.startswith("('via'"):
        tup = ast.literal_eval(line)
        if math.hypot(tup[2] / MM - J2C[0], tup[3] / MM - J2C[1]) > 11:
            far.append(line)
print("track diffs farther than 11mm from old J2 centre:", len(far))
for line in far[:10]:
    print("  FAR", line[:120])

# outline mirror symmetry check: every left element must mirror a right element
edges = []
for d in b10.GetDrawings():
    if d.GetLayer() == p.Edge_Cuts:
        s, e = d.GetStart(), d.GetEnd()
        edges.append(((s.x, s.y), (e.x, e.y)))
print("outline elements:", len(edges))
eset = set()
for (a, bb) in edges:
    eset.add((a, bb)); eset.add((bb, a))
bad = 0
for (a, bb) in edges:
    m = ((200_000_000 - bb[0], bb[1]), (200_000_000 - a[0], a[1]))
    if m not in eset:
        bad += 1
        print("  outline element without mirror twin:", a, bb)
print("outline mirror-complete:", bad == 0)
(RT / "rev10-verify.json").write_text(json.dumps({
    "census_rev9": len(c9), "census_rev10": len(c10), "census_diff": len(set(c9) ^ set(c10)),
    "j3_identical": j3_9 == j3_10, "far_track_diffs": len(far), "outline_mirror_complete": bad == 0}, indent=1))
