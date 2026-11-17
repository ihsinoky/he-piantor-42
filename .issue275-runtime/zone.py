"""Dump all copper items in a box around a site."""
import sys
from pathlib import Path
import pcbnew as p

MM = 1e6
SRC = Path("/home/hatch/workspace/projects/he-piantor-mainsym/hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb")
b = p.LoadBoard(str(SRC))
cx, cy, r = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])

def inbox(x, y):
    return abs(x - cx) <= r and abs(y - cy) <= r

n = 0
for t in b.GetTracks():
    s, e = t.GetStart(), t.GetEnd()
    x1, y1, x2, y2 = s.x / MM, s.y / MM, e.x / MM, e.y / MM
    if inbox(x1, y1) or inbox(x2, y2):
        kind = "via" if isinstance(t, p.PCB_VIA) else "trk"
        w = t.GetWidth(p.F_Cu) / MM if kind == "via" else t.GetWidth() / MM
        print(f"{kind} {t.m_Uuid.AsString()[:8]} net={t.GetNetname():<10} L{t.GetLayer()} w={w:.2f} ({x1:.3f},{y1:.3f})->({x2:.3f},{y2:.3f})")
        n += 1
print("items:", n)
for fp in b.GetFootprints():
    pp = fp.GetPosition()
    if inbox(pp.x / MM, pp.y / MM):
        print("FP", fp.GetReference(), pp.x / MM, pp.y / MM, fp.GetOrientationDegrees())
