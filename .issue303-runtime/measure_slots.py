#!/usr/bin/env python3
"""Issue #303 revision, step 0 (reproduce): measure the CURRENT Stage 2
board against the case 3D fin-slot rectangles (board-local coords).

Reports every footprint pad / track / via whose copper intersects a slot
rectangle (the board as saved would be milled there), plus the J1 housing
envelope vs the east fin volume (the case note's 10.09 mm3 figure)."""
import pcbnew

PCB = "/home/hatch/workspace/projects/he-piantor-pwr/hardware/kicad/qualification/issue-303-pwr/pwr.kicad_pcb"
b = pcbnew.LoadBoard(PCB)

SLOTS = {
    "W-S": (3.75, 53.50, 19.75, 56.15),
    "E-S": (32.75, 53.50, 48.75, 56.15),
    "N-notch": (17.75, 0.00, 34.75, 2.50),
}
FINS = {  # fin solid inside each slot (slot shrunk by the 0.5 clearance)
    "W-S": (4.25, 54.00, 19.25, 55.65),
    "E-S": (33.25, 54.00, 48.25, 55.65),
    "N-notch": (18.25, 0.35, 34.25, 2.00),
}

def overlap(a, r):
    return a[0] < r[2] and a[2] > r[0] and a[1] < r[3] and a[3] > r[1]

def mm(v):
    return v / 1e6

hits = []
for fp in b.GetFootprints():
    ref = fp.GetReference()
    for pad in fp.Pads():
        bb = pad.GetBoundingBox()
        box = (mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom()))
        for name, r in SLOTS.items():
            if overlap(box, r):
                hits.append(f"PAD {ref}.{pad.GetNumber()} net={pad.GetNetname()} bbox={tuple(round(v,2) for v in box)} x slot {name}")
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T:
        p = t.GetPosition()
        x, y, rad = mm(p.x), mm(p.y), t.GetWidth() / 2e6
        box = (x - rad, y - rad, x + rad, y + rad)
        for name, r in SLOTS.items():
            if overlap(box, r):
                hits.append(f"VIA net={t.GetNetname()} at ({x:.2f},{y:.2f}) r={rad:.2f} x slot {name}")
    else:
        s, e = t.GetStart(), t.GetEnd()
        x1, y1, x2, y2 = mm(s.x), mm(s.y), mm(e.x), mm(e.y)
        hw = t.GetWidth() / 2e6
        box = (min(x1, x2) - hw, min(y1, y2) - hw, max(x1, x2) + hw, max(y1, y2) + hw)
        for name, r in SLOTS.items():
            if overlap(box, r):
                # segment-vs-rect: bbox overlap is enough to flag for hand check
                hits.append(f"TRACK net={t.GetNetname()} layer={t.GetLayerName()} ({x1:.2f},{y1:.2f})->({x2:.2f},{y2:.2f}) w={2*hw:.2f} bbox x slot {name}")

print("== copper x slot-rect intersections on the CURRENT board ==")
for h in hits:
    print(" ", h)
print(f"({len(hits)} flagged items)")

# J1 housing envelope (Stage 2 note: body ~5.7 wide centred on J1, GH class
# depth ~4.7, height 2.9) vs the east fin solid -> the case note's figure
j1 = b.FindFootprintByReference("J1")
p = j1.GetPosition()
cx, cy = mm(p.x), mm(p.y)
housing = (cx - 2.85, cy - 2.35, cx + 2.85, cy + 2.35)
fin = FINS["E-S"]
ix = max(0.0, min(housing[2], fin[2]) - max(housing[0], fin[0]))
iy = max(0.0, min(housing[3], fin[3]) - max(housing[1], fin[1]))
fin_top_z, board_top_z = 10.5, 0.15  # case frame; housing Z 0.15..3.05
iz = max(0.0, min(3.05, fin_top_z) - board_top_z)
print(f"J1 housing envelope {tuple(round(v,2) for v in housing)} x E fin "
      f"{fin}: plan overlap {ix:.2f} x {iy:.2f} mm, Z overlap {iz:.2f} mm "
      f"-> {ix*iy*iz:.2f} mm3 (case note: 10.09 mm3 with their exact envelope)")
