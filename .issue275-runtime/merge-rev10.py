"""Merge KRT output into the prep board by zone replacement:
within R of the old J2 centre, the 9 J2 nets' copper := KRT's copper;
everywhere else the prep board (= Rev.9 + outline + J2 move + stub rip)
is untouched. Then refill, census-diff vs Rev.9, save."""
import json, math, sys, ast
from pathlib import Path
import pcbnew as p

MM = 1e6
RT = Path("/home/hatch/workspace/projects/he-piantor-mainsym/.issue275-runtime")
TREE = Path("/home/hatch/workspace/projects/he-piantor-mainsym/hardware/kicad/qualification/issue-275-main-rev10/main-rev10")
BOARD = TREE / "main.kicad_pcb"
REV9 = Path("/home/hatch/workspace/projects/he-piantor-mainsym/hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb")
ROUTED = RT / "rev10-routed.kicad_pcb"
R = float(sys.argv[1]) if len(sys.argv) > 1 else 10.0
J2C = (76.048074, 112.073215)
NETS = {'GND', 'HALL_5V', 'MUX_A0', 'MUX_A1', 'MUX_A2', 'MUX_OUT_A', 'MUX_OUT_B', 'MUX_OUT_C', 'WING_EN'}

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

def inzone_nm(x, y):
    return math.hypot(x / MM - J2C[0], y / MM - J2C[1]) <= R

# 1) snapshot KRT zone copper as plain data
bk = p.LoadBoard(str(ROUTED))
kdata = []
kkeys = set()
for t in bk.GetTracks():
    if t.GetNetname() not in NETS:
        continue
    s, e = t.GetStart(), t.GetEnd()
    if inzone_nm(s.x, s.y) or inzone_nm(e.x, e.y):
        if isinstance(t, p.PCB_VIA):
            rec = ("via", t.GetNetname(), (s.x, s.y), t.GetWidth(p.F_Cu), t.GetDrillValue(), t.GetViaType())
            key = ("via", t.GetNetname(), (s.x, s.y), t.GetWidth(p.F_Cu), t.GetDrillValue())
        else:
            rec = ("trk", t.GetNetname(), (s.x, s.y), (e.x, e.y), t.GetWidth(), t.GetLayer())
            key = ("trk", t.GetNetname(), (s.x, s.y), (e.x, e.y), t.GetWidth(), t.GetLayer())
        kdata.append(rec)
        kkeys.add(key)
print("KRT zone items snapshotted:", len(kdata))
del bk

# 2) census of Rev.9
b9 = p.LoadBoard(str(REV9))
before = census(b9)
del b9

# 3) modify prep board
b = p.LoadBoard(str(BOARD))
netobjs = {}
for t in b.GetTracks():
    netobjs.setdefault(t.GetNetname(), t.GetNet())
# single snapshot pass: decide removals and surviving keys from snapshot data only
snap = []
for t in list(b.GetTracks()):
    if t.GetNetname() in NETS:
        s, e = t.GetStart(), t.GetEnd()
        if inzone_nm(s.x, s.y) or inzone_nm(e.x, e.y):
            if isinstance(t, p.PCB_VIA):
                key = ("via", t.GetNetname(), (s.x, s.y), t.GetWidth(p.F_Cu), t.GetDrillValue())
            else:
                key = ("trk", t.GetNetname(), (s.x, s.y), (e.x, e.y), t.GetWidth(), t.GetLayer())
            snap.append((t, key))
removed = 0
kept_identical = 0
prep_keys = set()
for (t, key) in snap:
    if key in kkeys:
        kept_identical += 1
        prep_keys.add(key)  # KRT kept this item geometrically identical: preserve original (and UUID)
    else:
        b.Remove(t); removed += 1
print("zone copper removed from prep:", removed, "| identical items preserved:", kept_identical)
_keep = []
added = 0
skipped_dup = 0
for rec in kdata:
    if rec[0] == "via":
        key = ("via", rec[1], rec[2], rec[3], rec[4])
    else:
        key = ("trk", rec[1], rec[2], rec[3], rec[4], rec[5])
    if key in prep_keys:
        skipped_dup += 1
        continue
    if rec[0] == "via":
        _, net, pos, w, drill, vtype = rec
        nt = p.PCB_VIA(b)
        nt.SetPosition(p.VECTOR2I(*pos))
        nt.SetWidth(w); nt.SetDrill(drill); nt.SetViaType(vtype)
    else:
        _, net, sp, ep, w, layer = rec
        nt = p.PCB_TRACK(b)
        nt.SetStart(p.VECTOR2I(*sp)); nt.SetEnd(p.VECTOR2I(*ep))
        nt.SetWidth(w); nt.SetLayer(layer)
    nt.SetNet(netobjs[net])
    b.Add(nt); _keep.append(nt); added += 1
print("zone copper added from KRT:", added, "| duplicates skipped:", skipped_dup)

filler = p.ZONE_FILLER(b)
filler.Fill(b.Zones())
b.BuildConnectivity()
(RT / "rev10-merge.json").write_text(json.dumps({"R": R, "removed": removed, "added": added,
                                                 "census_before": len(before)}, indent=1))
b.Save(str(BOARD))
print("saved merged Rev.10 board (census verification runs as a separate process)")
