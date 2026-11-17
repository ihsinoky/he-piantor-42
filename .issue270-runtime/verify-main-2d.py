"""Verify Main Rev.9 stage 2d: (1) non-Edge.Cuts census identical to
the committed Stage 2b board (from git), (2) KiCad-assembled outline
matches the design polygon (stage2d-polys.json) in board frame."""
import json, subprocess, sys
from pathlib import Path
import pcbnew as p
from shapely.geometry import Polygon

MM = 1e6
RT = Path("/home/hatch/workspace/projects/he-piantor-mainoutline/.issue270-runtime")
WT = Path("/home/hatch/workspace/projects/he-piantor-mainoutline")
REL = "hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb"

def outline_kicad(board):
    ps = p.SHAPE_POLY_SET(); board.GetBoardPolygonOutlines(ps)
    ch = ps.Outline(0)
    return Polygon([(ch.CPoint(j).x / MM, ch.CPoint(j).y / MM) for j in range(ch.PointCount())])

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

old = subprocess.run(["git", "-C", str(WT), "show", f"HEAD:{REL}"], capture_output=True, check=True).stdout
(RT / "rev9-2b.kicad_pcb").write_bytes(old)
b_old = p.LoadBoard(str(RT / "rev9-2b.kicad_pcb"))
b_new = p.LoadBoard(str(WT / REL))
c_old, c_new = census(b_old), census(b_new)
print("census: 2b =", len(c_old), " 2d =", len(c_new), " identical:", c_old == c_new)
assert c_old == c_new
new_poly = outline_kicad(b_new)
design = Polygon(json.loads((RT / "stage2d-polys.json").read_text())["main_final"])
design_board = Polygon([(x + 100.0, y + 70.0) for x, y in design.exterior.coords])
sd = new_poly.symmetric_difference(design_board)
print(f"outline: board {new_poly.area:.3f} mm2, design {design_board.area:.3f} mm2, symdiff {sd.area:.5f} mm2")
assert sd.area < 0.05
old_poly = outline_kicad(b_old)
print(f"area change vs 2b Rev.9: {new_poly.area - old_poly.area:+.3f} mm2 (2b area {old_poly.area:.3f})")
print("MAIN 2D VERIFY OK")
