#!/usr/bin/env python3
"""Issue #303 Stage 2 + fixing-revision checker: series topology +
geometry on the ROUTED board.

Loads pwr.kicad_pcb as saved (no refill, no edits) and asserts:
 1. pad->net map equals the Stage 1 topology (topology.json semantics)
 2. series walk J1.2 -> BT1 -> BT2 -> BT3 -> F1 -> J2 -> J1.1 visits each
    cell exactly once; no net touches both terminals of any cell
 3. outline bbox is exactly 52.5 x 58.0 mm
 4. cell centres; POSITIVE contact pads span their +-26.00 mm face line;
    NEGATIVE ends: the case fin is the contact land -- the fin slot edge
    sits 0.50 beyond the face line (fin face ON the line) and the ear
    pad ends 0.25 clear of the slot edge
 5. the three fin slots exist in Edge.Cuts at the case-3D coordinates
    (board-local): W/E south rects + north open notch
 6. no footprint pad within 0.2 of a slot rect; no via copper within 0.2
 7. tongue strips (E/W edge strips, case #296): no pad / via inside
 8. J1 pads inside the case-verified envelope (local X 23.25..29.25,
    Y 55.07..58.0); F1 pads inside theirs (X 6.25..9.45, Y 56.37..57.97)
 9. east tab column (x >= 48.75, y 17.4..53.7) holds no pads except TP1,
    no vias
10. all three pours carry stored fill; no stored fill inside the slots
"""
import json
import pcbnew

PCB = "/home/hatch/workspace/projects/he-piantor-pwr/hardware/kicad/qualification/issue-303-pwr/pwr.kicad_pcb"
b = pcbnew.LoadBoard(PCB)
fails = []

def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)

pads = {}   # (ref, pin) -> (netname, x_mm, y_mm, w_mm, h_mm) board-frame
for fp in b.GetFootprints():
    ref = fp.GetReference()
    for pad in fp.Pads():
        # board-frame bbox (pad.GetSize() is footprint-local and swaps
        # axes under 90-degree rotation -- J2 caught this in rev A)
        bb = pad.GetBoundingBox()
        x0, y0 = bb.GetX() / 1e6, bb.GetY() / 1e6
        w, h = bb.GetWidth() / 1e6, bb.GetHeight() / 1e6
        pads[(ref, pad.GetNumber())] = (
            pad.GetNetname(), x0 + w / 2, y0 + h / 2, w, h)

expected = {
    ("J1", "1"): "VBAT_OUT", ("J1", "2"): "PACK_NEG",
    ("BT1", "1"): "BRIDGE_N", ("BT1", "2"): "PACK_NEG",
    ("BT2", "1"): "BRIDGE_S", ("BT2", "2"): "BRIDGE_N",
    ("BT3", "1"): "PACK_POS_RAW", ("BT3", "2"): "BRIDGE_S",
    ("F1", "1"): "PACK_POS_RAW", ("F1", "2"): "PACK_POS_FUSED",
    ("J2", "1"): "PACK_POS_FUSED", ("J2", "2"): "VBAT_OUT",
    ("TP1", "1"): "PACK_POS_RAW", ("TP2", "1"): "PACK_NEG",
}
for k, net in expected.items():
    got = pads.get(k, (None,))[0]
    check(got == net, f"pad {k} net == {net} (got {got})")

# series walk over components: each component maps its two pad nets
comp_nets = {}
for (ref, pin), (net, *_rest) in pads.items():
    comp_nets.setdefault(ref, []).append(net)
seq = [pads[("J1", "2")][0]]
cur_comp, cur_net = "J1", seq[0]
for nxt in ["BT1", "BT2", "BT3", "F1", "J2"]:
    shared = set(comp_nets[cur_comp]) & set(comp_nets[nxt])
    check(shared == {cur_net}, f"{cur_comp}->{nxt} entered via {cur_net} (shared {shared})")
    others = [n for n in comp_nets[nxt] if n != cur_net]
    check(len(others) == 1, f"{nxt} exits via exactly one other net {others}")
    cur_net = others[0]
    seq.append(cur_net)
    cur_comp = nxt
check(pads[("J1", "1")][0] == cur_net, "walk ends at J1.1 net VBAT_OUT")
check(seq == ["PACK_NEG", "BRIDGE_N", "BRIDGE_S", "PACK_POS_RAW",
              "PACK_POS_FUSED", "VBAT_OUT"], f"series net order {seq}")
for cell in ["BT1", "BT2", "BT3"]:
    check(comp_nets[cell][0] != comp_nets[cell][1],
          f"{cell} terminals on distinct nets {comp_nets[cell]}")

# outline bbox + slot geometry from Edge.Cuts segments
segs = set()
xs, ys = [], []
for d in b.GetDrawings():
    if d.GetLayer() == pcbnew.Edge_Cuts:
        s, e = d.GetStart(), d.GetEnd()
        p1 = (round(s.x / 1e6, 3), round(s.y / 1e6, 3))
        p2 = (round(e.x / 1e6, 3), round(e.y / 1e6, 3))
        segs.add((p1, p2)); segs.add((p2, p1))
        xs += [p1[0], p2[0]]; ys += [p1[1], p2[1]]
w, h = max(xs) - min(xs), max(ys) - min(ys)
check(abs(w - 52.5) < 0.01 and abs(h - 58.0) < 0.01, f"outline {w:.2f} x {h:.2f} mm")

SLOTS = {"W-S": (3.75, 53.50, 19.75, 56.15), "E-S": (32.75, 53.50, 48.75, 56.15)}
NOTCH = (17.75, 0.0, 34.75, 2.50)
for name, (x0, y0, x1, y1) in SLOTS.items():
    for side in [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
                 ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]:
        check(side in segs, f"slot {name} side {side} in Edge.Cuts")
for side in [((17.75, 0.0), (17.75, 2.5)), ((17.75, 2.5), (34.75, 2.5)),
             ((34.75, 2.5), (34.75, 0.0))]:
    check(side in segs, f"north notch side {side} in Edge.Cuts")

# cell centres + contact faces
centres = {"BT1": (11.25, 28.0), "BT2": (26.25, 28.0), "BT3": (41.25, 28.0)}
for ref, (cx, cy) in centres.items():
    fp = b.FindFootprintByReference(ref)
    p = fp.GetPosition()
    check(abs(p.x / 1e6 - cx) < 0.01 and abs(p.y / 1e6 - cy) < 0.01,
          f"{ref} centre ({p.x/1e6:.2f},{p.y/1e6:.2f})")
    # pin 1 = positive end: pad spans the face line
    net, x, y, pw, ph = pads[(ref, "1")]
    face = cy - 26.0 if y < cy else cy + 26.0
    check(y - ph / 2 <= face <= y + ph / 2,
          f"{ref}.1 (+) pad y-span [{y-ph/2:.2f},{y+ph/2:.2f}] covers face {face:.2f}")
    # pin 2 = negative end: fin land. Pad ends 0.25 clear of the slot
    # edge; the slot edge sits 0.50 beyond the face (fin face ON it).
    net, x, y, pw, ph = pads[(ref, "2")]
    if y > cy:   # south negative (BT1, BT3): slot north edge 53.50
        slot_edge = y + ph / 2 + 0.25
        fin_face = slot_edge + 0.50
        check(abs(slot_edge - 53.50) < 0.01 and abs(fin_face - (cy + 26.0)) < 0.01,
              f"{ref}.2 (-) pad ends 0.25 clear of slot edge {slot_edge:.2f}; fin face {fin_face:.2f} == face {cy+26.0:.2f}")
    else:        # north negative (BT2): notch floor 2.50
        slot_edge = y - ph / 2 - 0.25
        fin_face = slot_edge - 0.50
        check(abs(slot_edge - 2.50) < 0.01 and abs(fin_face - (cy - 26.0)) < 0.01,
              f"{ref}.2 (-) pad ends 0.25 clear of notch floor {slot_edge:.2f}; fin face {fin_face:.2f} == face {cy-26.0:.2f}")

def box_overlap(a, r, grow=0.0):
    return (a[0] < r[2] + grow and a[2] > r[0] - grow and
            a[1] < r[3] + grow and a[3] > r[1] - grow)

ALL_SLOTS = dict(SLOTS); ALL_SLOTS["N-notch"] = NOTCH
for (ref, pin), (net, x, y, pw, ph) in pads.items():
    box = (x - pw / 2, y - ph / 2, x + pw / 2, y + ph / 2)
    for name, r in ALL_SLOTS.items():
        check(not box_overlap(box, r, 0.19),
              f"pad {ref}.{pin} >=0.2 clear of slot {name}")
vias = []
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T:
        p = t.GetPosition()
        vias.append((p.x / 1e6, p.y / 1e6))
for (x, y) in vias:
    for name, (x0, y0, x1, y1) in ALL_SLOTS.items():
        check(not (x0 - 0.49 < x < x1 + 0.49 and y0 - 0.49 < y < y1 + 0.49),
              f"via ({x:.1f},{y:.1f}) copper >=0.2 clear of slot {name}")
    check(not (x >= 48.75 and 17.4 <= y <= 53.7), f"via ({x:.1f},{y:.1f}) outside east tab column")

# tongue strips: no pads / vias inside
STRIPS = [(0.0, 9.37, 0.5, 15.37), (0.0, 39.37, 0.5, 45.37),
          (52.0, 9.37, 52.5, 15.37), (52.0, 39.37, 52.5, 45.37)]
for (ref, pin), (net, x, y, pw, ph) in pads.items():
    box = (x - pw / 2, y - ph / 2, x + pw / 2, y + ph / 2)
    for r in STRIPS:
        check(not box_overlap(box, r), f"pad {ref}.{pin} outside tongue strip {r}")
    if x >= 48.75 and 17.4 <= y <= 53.7:
        check(ref == "TP1", f"east tab column pad is TP1 only (found {ref}.{pin})")
for (x, y) in vias:
    for r in STRIPS:
        check(not (r[0] - 0.3 < x < r[2] + 0.3 and r[1] - 0.3 < y < r[3] + 0.3),
              f"via ({x:.1f},{y:.1f}) outside tongue strip {r}")

# J1 / F1 case-verified envelopes
for pin in ["1", "2"]:
    net, x, y, pw, ph = pads[("J1", pin)]
    check(23.25 <= x - pw / 2 and x + pw / 2 <= 29.25 and
          55.07 <= y - ph / 2 and y + ph / 2 <= 58.0,
          f"J1.{pin} pad inside case envelope (x {x-pw/2:.2f}..{x+pw/2:.2f}, y {y-ph/2:.2f}..{y+ph/2:.2f})")
    net, x, y, pw, ph = pads[("F1", pin)]
    check(6.25 <= x - pw / 2 and x + pw / 2 <= 9.45 and
          56.37 <= y - ph / 2 and y + ph / 2 <= 57.97,
          f"F1.{pin} pad inside case envelope (x {x-pw/2:.2f}..{x+pw/2:.2f}, y {y-ph/2:.2f}..{y+ph/2:.2f})")

zones = {z.GetNetname(): z for z in b.Zones()}
for name in ["BRIDGE_N", "BRIDGE_S", "PACK_POS_RAW"]:
    z = zones.get(name)
    ok = z is not None and z.GetFilledPolysList(pcbnew.F_Cu).OutlineCount() > 0
    check(ok, f"zone (net {name}) present with stored fill")

# no stored zone fill inside the slot rects (probe points: centre,
# corners inset 0.05, and points 0.18 outside each edge midpoint)
def probes(r):
    x0, y0, x1, y1 = r
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    pts = [(cx, cy), (x0 + 0.05, y0 + 0.05), (x1 - 0.05, y0 + 0.05),
           (x0 + 0.05, y1 - 0.05), (x1 - 0.05, y1 - 0.05),
           (cx, y0 - 0.18), (cx, y1 + 0.18), (x0 - 0.18, cy), (x1 + 0.18, cy)]
    return [(pcbnew.VECTOR2I(int(px * 1e6), int(py * 1e6))) for px, py in pts]
for name, r in ALL_SLOTS.items():
    for zname, z in zones.items():
        filled = z.GetFilledPolysList(pcbnew.F_Cu)
        for pt in probes(r):
            inside = any(filled.Outline(oi).PointInside(pt)
                         for oi in range(filled.OutlineCount()))
            check(not inside,
                  f"zone {zname} fill clear of slot {name} probe ({pt.x/1e6:.2f},{pt.y/1e6:.2f})")

print("\n%d checks failed" % len(fails))
raise SystemExit(1 if fails else 0)
