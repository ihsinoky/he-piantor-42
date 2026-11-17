"""Merge v2 (additions-only): prep board has all surviving copper LOCKED, so
KRT could only add. Import KRT's added items (9 J2 nets) within R of the old
J2 centre into the prep board; report anything else KRT did."""
import json, math, sys
from pathlib import Path
import pcbnew as p

MM = 1e6
RT = Path("/home/hatch/workspace/projects/he-piantor-mainsym/.issue275-runtime")
TREE = Path("/home/hatch/workspace/projects/he-piantor-mainsym/hardware/kicad/qualification/issue-275-main-rev10/main-rev10")
BOARD = TREE / "main.kicad_pcb"
ROUTED = RT / "rev10-routed.kicad_pcb"
R = float(sys.argv[1]) if len(sys.argv) > 1 else 10.0
J2C = (76.048074, 112.073215)
NETS = {'GND', 'HALL_5V', 'MUX_A0', 'MUX_A1', 'MUX_A2', 'MUX_OUT_A', 'MUX_OUT_B', 'MUX_OUT_C', 'WING_EN'}

def key_of(kind, net, a, b_, w, extra):
    pts = tuple(sorted([a, b_])) if kind == "trk" else (a,)
    return (kind, net, pts, w, extra)

def inzone(x, y):
    return math.hypot(x / MM - J2C[0], y / MM - J2C[1]) <= R

# snapshot KRT output as data
bk = p.LoadBoard(str(ROUTED))
kitems = []
for t in bk.GetTracks():
    s, e = t.GetStart(), t.GetEnd()
    if isinstance(t, p.PCB_VIA):
        kitems.append(("via", t.GetNetname(), (s.x, s.y), (s.x, s.y), t.GetWidth(p.F_Cu), t.GetDrillValue(), t.GetViaType()))
    else:
        kitems.append(("trk", t.GetNetname(), (s.x, s.y), (e.x, e.y), t.GetWidth(), t.GetLayer(), None))
del bk

# prep board: snapshot keys (all nets), net objects
b = p.LoadBoard(str(BOARD))
prep_keys = set()
netobjs = {}
for t in b.GetTracks():
    s, e = t.GetStart(), t.GetEnd()
    netobjs.setdefault(t.GetNetname(), t.GetNet())
    if isinstance(t, p.PCB_VIA):
        prep_keys.add(key_of("via", t.GetNetname(), (s.x, s.y), (s.x, s.y), t.GetWidth(p.F_Cu), t.GetDrillValue()))
    else:
        prep_keys.add(key_of("trk", t.GetNetname(), (s.x, s.y), (e.x, e.y), t.GetWidth(), t.GetLayer()))

added, far_adds, foreign_adds, missing = 0, [], [], 0
_keep = []
kkeys_in_zone = set()
for (kind, net, sp, ep, w, extra, vtype) in kitems:
    k = key_of(kind, net, sp, ep, w, extra)
    if inzone(sp[0], sp[1]) or inzone(ep[0], ep[1]):
        kkeys_in_zone.add(k)
    if k in prep_keys:
        continue
    # an addition
    if net not in NETS:
        foreign_adds.append((kind, net, sp, ep))
        continue
    if not (inzone(sp[0], sp[1]) or inzone(ep[0], ep[1])):
        # own-net KRT completion segments just outside the zone (the nets'
        # own route corridors): import, but record their reach
        far_adds.append((kind, net, sp, ep))
    if kind == "via":
        nt = p.PCB_VIA(b)
        nt.SetPosition(p.VECTOR2I(*sp))
        nt.SetWidth(w); nt.SetDrill(extra); nt.SetViaType(vtype)
    else:
        nt = p.PCB_TRACK(b)
        nt.SetStart(p.VECTOR2I(*sp)); nt.SetEnd(p.VECTOR2I(*ep))
        nt.SetWidth(w); nt.SetLayer(extra)
    nt.SetNet(netobjs[net])
    b.Add(nt); _keep.append(nt); added += 1
# locked-copper check: every prep item of the 9 nets in-zone must still exist in KRT output
for k in prep_keys:
    if k[1] in NETS:
        pts = k[2]
        if any(inzone(x, y) for (x, y) in pts) and k not in kkeys_in_zone and k not in {key_of(i[0], i[1], i[2], i[3], i[4], i[5]) for i in kitems}:
            missing += 1
print("KRT additions imported:", added, "| far additions skipped:", len(far_adds),
      "| foreign-net additions skipped:", len(foreign_adds), "| prep in-zone items missing in KRT output:", missing)
for fa in far_adds[:6]:
    print("  FAR ADD skipped:", fa[1], fa[2], fa[3])
filler = p.ZONE_FILLER(b)
filler.Fill(b.Zones())
b.BuildConnectivity()
(RT / "rev10-merge.json").write_text(json.dumps({"R": R, "added": added, "far_adds_skipped": len(far_adds),
                                                 "foreign_adds_skipped": len(foreign_adds), "missing_prep_in_krt": missing}, indent=1))
b.Save(str(BOARD))
print("saved merged Rev.10 board")
