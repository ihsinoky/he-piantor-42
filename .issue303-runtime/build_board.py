#!/usr/bin/env python3
"""Issue #303 Stage 2 + fixing revision: build pwr.kicad_pcb from the
Stage 1 schematic's net assignment. Geometry per
.issue303-runtime/plan-stage2.md and plan-revision.md (board-local frame:
origin NW corner, +x east, +y south, board 52.5 x 58.0, 2 layers).

Revision (Issue #296 case 3D fixing decision): three fin slots (W/E south
rects + north open notch), J1 into the south-edge free band, F1 into the
case-verified SW envelope, J2 beside J1 for the south-wall switch run,
BT negative pads trimmed to the fin-slot edges."""
import pcbnew, sys

LIB = "/home/hatch/workspace/projects/he-piantor-pwr/hardware/kicad/qualification/issue-303-pwr/pwr.pretty"
OUT = "/home/hatch/workspace/projects/he-piantor-pwr/hardware/kicad/qualification/issue-303-pwr/pwr.kicad_pcb"
MM = pcbnew.FromMM
def V(x, y): return pcbnew.VECTOR2I(MM(x), MM(y))

board = pcbnew.BOARD()
ds = board.GetDesignSettings()
try:
    nc = board.GetAllNetClasses()['Default']
    nc.SetClearance(MM(0.2))
    nc.SetTrackWidth(MM(0.4))
    nc.SetViaDiameter(MM(0.6))
    nc.SetViaDrill(MM(0.3))
except Exception as e:
    print("netclass setup:", e)
try:
    ds.m_CopperEdgeClearance = MM(0.2)
except Exception as e:
    print("edge clearance:", e)

NETS = {}
def net(name):
    if name not in NETS:
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
        NETS[name] = n
    return NETS[name]

CONN = {  # schematic pad->net (topology.json, Stage 1 proof)
    ("BT1","1"):"BRIDGE_N", ("BT1","2"):"PACK_NEG",
    ("BT2","1"):"BRIDGE_S", ("BT2","2"):"BRIDGE_N",
    ("BT3","1"):"PACK_POS_RAW", ("BT3","2"):"BRIDGE_S",
    ("F1","1"):"PACK_POS_RAW", ("F1","2"):"PACK_POS_FUSED",
    ("J1","1"):"VBAT_OUT", ("J1","2"):"PACK_NEG",
    ("J2","1"):"PACK_POS_FUSED", ("J2","2"):"VBAT_OUT",
    ("TP1","1"):"PACK_POS_RAW", ("TP2","1"):"PACK_NEG",
}

# outline 52.5 x 58.0 with the north fin notch (X 17.75..34.75, 2.50 deep)
def seg(x1, y1, x2, y2):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(V(x1, y1)); s.SetEnd(V(x2, y2))
    s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.05))
    board.Add(s)
for (x1, y1, x2, y2) in [
        (0, 0, 17.75, 0), (17.75, 0, 17.75, 2.5), (17.75, 2.5, 34.75, 2.5),
        (34.75, 2.5, 34.75, 0), (34.75, 0, 52.5, 0),
        (52.5, 0, 52.5, 58), (52.5, 58, 0, 58), (0, 58, 0, 0)]:
    seg(x1, y1, x2, y2)
# fin slots: W (3.75..19.75, 53.50..56.15), E (32.75..48.75, 53.50..56.15)
for (sx0, sy0, sx1, sy1) in [(3.75, 53.5, 19.75, 56.15),
                            (32.75, 53.5, 48.75, 56.15)]:
    for (x1, y1, x2, y2) in [(sx0, sy0, sx1, sy0), (sx1, sy0, sx1, sy1),
                             (sx1, sy1, sx0, sy1), (sx0, sy1, sx0, sy0)]:
        seg(x1, y1, x2, y2)

FPS = [  # ref, lib name, x, y, rot(deg)
    ("BT1","CELL_AA_CONTACT_PAIR",11.25,28.0,0),
    ("BT2","CELL_AA_CONTACT_PAIR",26.25,28.0,180),
    ("BT3","CELL_AA_CONTACT_PAIR",41.25,28.0,0),
    ("F1","PTC_1206",7.85,57.17,0),
    ("J1","GH_2P",26.25,56.9,0),
    ("J2","SW_PADS_2P",20.2,57.075,90),
    ("TP1","TESTPOINT",51.0,30.0,0),
    ("TP2","TESTPOINT",2.5,56.6,0),
]
placed = {}
for ref, lib, x, y, rot in FPS:
    fp = pcbnew.FootprintLoad(LIB, lib)
    assert fp is not None, lib
    fp.SetReference(ref)
    fp.SetPosition(V(x,y))
    fp.SetOrientationDegrees(rot)
    board.Add(fp)
    placed[ref] = fp
    for pad in fp.Pads():
        num = pad.GetNumber()
        pad.SetNet(net(CONN[(ref,num)]))

# --- assertions on placed geometry (mm) ---
def padpos(ref, num):
    for pad in placed[ref].Pads():
        if pad.GetNumber() == num:
            p = pad.GetPosition()
            return (pcbnew.ToMM(p.x), pcbnew.ToMM(p.y))
    raise KeyError((ref,num))
exp = {("BT1","1"):(11.25,3.0),("BT1","2"):(11.25,51.775),
       ("BT2","1"):(26.25,53.0),("BT2","2"):(26.25,4.225),
       ("BT3","1"):(41.25,3.0),("BT3","2"):(41.25,51.775),
       ("F1","1"):(6.90,57.17),("F1","2"):(8.80,57.17),
       ("J1","1"):(25.625,56.9),("J1","2"):(26.875,56.9),
       ("J2","1"):(18.2,57.075),("J2","2"):(22.2,57.075),
       ("TP1","1"):(51.0,30.0),("TP2","1"):(2.5,56.6)}
for k, (ex, ey) in exp.items():
    ax, ay = padpos(*k)
    assert abs(ax-ex) < 0.01 and abs(ay-ey) < 0.01, (k, ax, ay, ex, ey)
print("pad placement assertions: PASS")

# --- zones (F.Cu) ---
def zone(netname, pts, prio=0):
    z = pcbnew.ZONE(board)
    z.SetLayer(pcbnew.F_Cu)
    z.SetNet(net(netname))
    z.SetLocalClearance(MM(0.25))
    z.SetMinThickness(MM(0.25))
    z.SetAssignedPriority(prio)
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    out = z.Outline()
    out.NewOutline()
    for (x,y) in pts:
        out.Append(MM(x), MM(y))
    board.Add(z)
    return z

# BRIDGE_N: stepped outline keeps the fill 0.25 clear of the north
# notch walls/floor (fill abutting a cut edge would fail edge clearance).
zone("BRIDGE_N", [(8.0,0.25),(17.5,0.25),(17.5,2.75),(30.5,2.75),
                  (30.5,6.2),(8.0,6.2)])
# BRIDGE_S: east lobe dropped in the revision (BT3- pad now ends at
# Y 53.25 and the east fin slot cuts the old lobe); west lobe kept for
# the BT2+ pad (spans to Y 55.7 in the fin-free band).
zone("BRIDGE_S", [(23.4,49.9),(44.1,49.9),(44.1,53.25),(29.1,53.25),
                  (29.1,55.75),(23.4,55.75)])
# PACK_POS_RAW: south end pulled back to Y 53.25 (0.25 clear of the
# east fin slot); the F1 feed via at (48.0, 50.6) is well north of it.
zone("PACK_POS_RAW", [(38.4,0.25),(52.25,0.25),(52.25,53.25),(47.5,53.25),
                      (47.5,46.9),(44.3,46.9),(44.3,5.9),(38.4,5.9)])

# --- tracks & vias ---
def track(netname, pts, width, layer):
    for (x1,y1),(x2,y2) in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(V(x1,y1)); t.SetEnd(V(x2,y2))
        t.SetWidth(MM(width)); t.SetLayer(layer); t.SetNet(net(netname))
        board.Add(t)
def via(netname, x, y):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(V(x,y))
    v.SetWidth(MM(0.6)); v.SetDrill(MM(0.3))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetNet(net(netname))
    board.Add(v)

FC, BC = pcbnew.F_Cu, pcbnew.B_Cu
# PACK_NEG: BT1.2/TP2 -> via(15.5,52.7) -> B.Cu east + south (B.Cu passes
# freely under the F.Cu-only BT2+ pad; an F.Cu jog at Y 55.2 shorted it in
# rev A -- caught by DRC) -> via(29.6,56.9) -> J1.2
track("PACK_NEG", [(2.5,52.7),(15.5,52.7)], 1.0, FC)
track("PACK_NEG", [(2.5,56.6),(2.5,52.7)], 0.6, FC)
via("PACK_NEG", 15.5, 52.7)
track("PACK_NEG", [(15.5,52.7),(29.6,52.7),(29.6,56.9)], 1.0, BC)
via("PACK_NEG", 29.6, 56.9)
track("PACK_NEG", [(29.6,56.9),(26.875,56.9)], 0.8, FC)
# PACK_POS_RAW feed: pour -> via(48,50.6) -> B.Cu west along Y 50.6 ->
# south at X 2.5 (west of the W slot) -> via(5.7,57.3) -> F1.1
via("PACK_POS_RAW", 48.0, 50.6)
track("PACK_POS_RAW", [(48.0,50.6),(2.5,50.6),(2.5,57.3),(5.7,57.3)], 1.0, BC)
via("PACK_POS_RAW", 5.7, 57.3)
track("PACK_POS_RAW", [(5.7,57.3),(6.90,57.17)], 0.6, FC)
# PACK_POS_FUSED: F1.2 -> J2.1 (F.Cu, south strip)
track("PACK_POS_FUSED", [(8.80,57.17),(18.2,57.075)], 0.8, FC)
# VBAT_OUT: J2.2 -> J1.1 (F.Cu)
track("VBAT_OUT", [(22.2,57.075),(25.625,56.9)], 0.5, FC)

# --- silkscreen: cell outlines + polarity marks; fixing on Dwgs.User ---
for fp in board.GetFootprints():
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
for cx in (11.25, 26.25, 41.25):
    r = pcbnew.PCB_SHAPE(board)
    r.SetShape(pcbnew.SHAPE_T_RECT)
    r.SetStart(V(cx-7.25, 6.5)); r.SetEnd(V(cx+7.25, 49.5))
    r.SetLayer(pcbnew.F_SilkS); r.SetWidth(MM(0.12)); r.SetFilled(False)
    board.Add(r)
def text(txt, x, y, size=1.2, layer=pcbnew.F_SilkS):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(txt); t.SetPosition(V(x,y))
    t.SetLayer(layer)
    t.SetTextSize(V(size, size)); t.SetTextThickness(MM(0.2))
    board.Add(t)
    return t
# positive-end marks at the contact rows (N: BT1+, BT3+ ; S: BT2+)
text("+", 11.25, 8.6); text("+", 41.25, 8.6); text("+", 26.25, 47.4)
t1 = text("TP1", 51.3, 24.5, 1.0)
t1.SetTextAngle(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))
text("TP2", 1.9, 54.3, 0.9)
def drect(x1, y1, x2, y2):
    r = pcbnew.PCB_SHAPE(board)
    r.SetShape(pcbnew.SHAPE_T_RECT)
    r.SetStart(V(x1, y1)); r.SetEnd(V(x2, y2))
    r.SetLayer(pcbnew.Dwgs_User); r.SetWidth(MM(0.1)); r.SetFilled(False)
    board.Add(r)
# tongue strips (E/W edges) + J1 free band, marked for the record
for (x1, y1, x2, y2) in [(0, 9.37, 0.5, 15.37), (0, 39.37, 0.5, 45.37),
                         (52.0, 9.37, 52.5, 15.37), (52.0, 39.37, 52.5, 45.37),
                         (19.75, 55.07, 32.75, 58.0)]:
    drect(x1, y1, x2, y2)
text("TONGUE KEEP-OUT (PADS/VIAS)", 26.25, 12.4, 1.0, pcbnew.Dwgs_User)
text("J1 BAND", 26.25, 55.6, 1.0, pcbnew.Dwgs_User)
text("FIN SLOTS: 3 (CASE #296)", 26.25, 51.0, 1.0, pcbnew.Dwgs_User)

pcbnew.SaveBoard(OUT, board)
# ZONE_FILLER segfaults on a freshly constructed BOARD in this kicad build;
# save -> LoadBoard -> Fill is the proven path (same as earlier rounds).
board2 = pcbnew.LoadBoard(OUT)
filler = pcbnew.ZONE_FILLER(board2)
ok = filler.Fill(board2.Zones())
assert ok, "zone fill failed"
board2.GetDesignSettings().m_HasStackup = True
pcbnew.SaveBoard(OUT, board2)
# 0.8 mm board: general thickness 1.6 -> 0.8, stackup core 1.51 -> 0.71
# (0.01 mask + 0.035 Cu + 0.71 core + 0.035 Cu + 0.01 mask = 0.80)
txt = open(OUT).read()
assert "(thickness 1.6)" in txt and "(thickness 1.51)" in txt
txt = txt.replace("(thickness 1.6)", "(thickness 0.8)", 1)
txt = txt.replace("(thickness 1.51)", "(thickness 0.71)", 1)
open(OUT, "w").write(txt)
b3 = pcbnew.LoadBoard(OUT)  # parse check after text edits
assert len(list(b3.GetFootprints())) == 8
print("saved + filled + 0.8mm stackup", OUT)
