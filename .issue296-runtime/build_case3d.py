"""Issue #296 Stage 3D — build the wireless case from the geometry17
body set + Stage B modifications. Run with the cad-venv python.
Frame: asm (X centred, +Y south), case Z (g17 Z - 2.65).
Outputs: hardware/case/issue-296-wireless/ (sources + STEP/STL) and
.issue296-runtime/asm3d/ (verification solids as BREP).
"""
import build123d as bd
import json, os, sys

G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
idx = json.load(open(G17 + "/index.json"))
pos = {e["name"]: i for i, e in enumerate(idx)}
OUT = os.path.expanduser("~/workspace/projects/he-piantor-case296b/hardware/case/issue-296-wireless")
ASM = os.path.expanduser("~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d")
os.makedirs(OUT, exist_ok=True)
os.makedirs(ASM, exist_ok=True)
ZC = 2.65

def load(name, dx=0.0):
    s = bd.import_brep(f"{G17}/{pos[name]}.brep")
    return s.moved(bd.Location((dx, 0, -ZC)))

def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))

def cyl(cx, cy, r, z0, z1):
    return bd.Solid.make_cylinder(r, z1 - z0, bd.Plane(origin=(cx, cy, z0)))

def fuse(*ss):
    r = ss[0]
    for s in ss[1:]:
        r = r.fuse(s)
    return r

def cut(s, *cs):
    for c in cs:
        s = s.cut(c)
    return s

def vol(s):
    return s.volume if hasattr(s, "volume") else sum(x.volume for x in s)

def report(name, s):
    bb = s.bounding_box()
    print(f"{name:16s} vol {vol(s)/1000:9.2f}k  X {bb.min.X:8.2f}..{bb.max.X:8.2f}"
          f"  Y {bb.min.Y:8.2f}..{bb.max.Y:8.2f}  Z {bb.min.Z:6.2f}..{bb.max.Z:6.2f}")
    return s

# ---------------------------------------------------------------- bays
BAY = dict(x=30.25, yn=-64.37, ys=-0.37)          # bay footprint
CAV = dict(x=28.25, yn=-62.37, ys=-2.37)          # cavity inner faces
FLR = -0.65                                       # levelled floor top
PB = dict(x=26.25, yn=-62.37, ys=-4.37, top=0.15)  # power board

# ================================================================ TRAYS
def build_tray(side):
    """side: +1 right, -1 left. Returns the modified tray solid."""
    sgn = 1 if side > 0 else -1
    t = load(f"tray-{'right' if sgn>0 else 'left'}", dx=9.5 * sgn)
    xa, xb = (-155.02, -6.0) if sgn < 0 else (13.0, 155.02)  # this half's X span (asm)
    # --- remove old Main H boss (lands at asm sgn*41.39, 64.40) ---
    t = cut(t, cyl(sgn * 41.39, 64.40, 5.0, FLR, 12.0))
    # --- add new Main H2/H3 boss at asm (sgn*31.89, 64.40), top = Main underside 4.70
    t = fuse(t, cyl(sgn * 31.89, 64.40, 4.0, FLR, 4.70))
    # --- bay: level cut inside footprint (this half's X slice) ---
    bx0, bx1 = max(-BAY["x"], xa), min(BAY["x"], xb)
    if bx1 > bx0:
        t = cut(t, box(bx0, bx1, BAY["yn"], BAY["ys"], FLR, 30.0))
        # floor slab + northward floor extension to the cavity face
        t = fuse(t, box(bx0, bx1, BAY["yn"], BAY["ys"], -2.65, FLR))
        # --- new north wall (Y -64.37..-62.37) up to cover underside 15.15;
        # capped at 7.80 over the middle cell's span (X -7.50..7.50): the
        # middle cell's north top corner sweeps Z >= 8.08 there when tipped
        # about its north contact point (verify E). Cover grows a skirt.
        nsegs = [(-30.25, -7.50, 15.15), (-7.50, 7.50, 7.80), (7.50, 30.25, 15.15)]
        for (na, nb, ntop) in nsegs:
            q0, q1 = max(na, bx0), min(nb, bx1)
            if q1 > q0:
                t = fuse(t, box(q0, q1, BAY["yn"], CAV["yn"], -2.65, ntop))
        # --- E/W wall (X sgn*(28.25..30.25)): stepped sill, tops from the
        # measured crossing scan (scan2.py): plate covers the band along the
        # whole bay (cap 9.15); finger span caps 7.40; the Wing board crosses
        # the band from Y -47 south (board bottom 4.70, underside bodies to
        # 3.30 physical / J_WING study envelope to -0.15) -> 2.45 sill over
        # Y -47..-20; board-only south of -20 -> 4.45.
        wx0, wx1 = (CAV["x"], BAY["x"]) if sgn > 0 else (-BAY["x"], -CAV["x"])
        for (wy0, wy1, wtop) in [(-62.37, -59.62, 9.15), (-59.62, -47.0, 7.40),
                                 (-47.0, -20.0, 2.45), (-20.0, -2.37, 4.45)]:
            t = fuse(t, box(wx0, wx1, wy0, wy1, FLR, wtop))
        # --- south wall of the bay (Y -2.37..-0.37): top 15.15 for
        # |X| <= 10.90; the Wing boards' south edges cross the wall band
        # from |X| ~11.14 out (measured tray x wings) -> sill 4.45 there
        # (board bottom 4.70 - 0.25); the plate cap 9.15 is looser.
        for (sx_lo, sx_hi, stop) in [(-30.25, -10.90, 4.45), (-10.90, 10.90, 15.15),
                                     (10.90, 30.25, 4.45)]:
            q0, q1 = max(sx_lo, bx0), min(sx_hi, bx1)
            if q1 > q0:
                t = fuse(t, box(q0, q1, CAV["ys"], BAY["ys"], FLR, stop))
        # --- 209 fins at spring sites (sliced at part boundary) ---
        # south fins: face at Y -8.37, extends south 1.65; X extent trimmed
        # to end at |X| 22.00 (clears Wing edge 22.50, plate clip 22.47 and
        # the Wing board's SW corner dip to |X| 22.14, measured)
        if sgn > 0:
            fx0, fx1 = max(7.0, bx0), min(22.00, bx1)
        else:
            fx0, fx1 = max(-22.00, bx0), min(-7.0, bx1)
        if fx1 > fx0:
            t = fuse(t, box(fx0, fx1, -8.37, -6.72, FLR, 10.5))
        # --- fixing tongues on the E/W wall inner face (Y -50, -20) ---
        tx0, tx1 = (25.75, CAV["x"]) if sgn > 0 else (-CAV["x"], -25.75)
        for ty in (-50.0, -20.0):
            t = fuse(t, box(tx0, tx1, ty - 3.0, ty + 3.0, PB["top"], 1.15))
        # --- cover screw pilot into the north wall top (this half's side)
        t = cut(t, cyl(sgn * 24.25, -63.37, 1.35, 10.0, 15.15))
    # --- south dent wall removal + straightening fill (this half's slice)
    sx0, sx1 = max(-50.0, xa), min(50.0, xb)
    if sx1 > sx0:
        t = cut(t, box(sx0, sx1, 68.4, 70.6, FLR, 11.0))          # old dent wall
        t = fuse(t, box(sx0, sx1, 70.0, 79.70, -2.65, FLR))       # band floor
        t = fuse(t, box(sx0, sx1, 79.70, 81.70, -2.65, 10.90))    # new south wall
    return report(f"tray-{'right' if sgn>0 else 'left'}", t)

tray_r = build_tray(+1)
tray_l = build_tray(-1)

# ================================================================ INFILL
def build_infill():
    xa, xb = -6.0, 13.0
    parts = []
    # bay slice: floor + north wall + south wall
    parts.append(box(xa, xb, BAY["yn"], BAY["ys"], -2.65, FLR))
    # north wall: capped 7.80 over the middle-cell span (see build_tray)
    parts.append(box(xa, 7.50, BAY["yn"], CAV["yn"], -2.65, 7.80))
    parts.append(box(7.50, xb, BAY["yn"], CAV["yn"], -2.65, 15.15))
    # south wall: 15.15 to |X| 10.90, then the Wing-crossing sill 4.45
    parts.append(box(xa, 10.90, CAV["ys"], BAY["ys"], FLR, 15.15))
    parts.append(box(10.90, xb, CAV["ys"], BAY["ys"], FLR, 4.45))
    # north fin (BT2-, centre (0,-60.37), face at -60.37 extends north 1.65),
    # sliced to this part: X -6..8 (rest belongs to tray-left build below)
    parts.append(box(xa, 8.0, -62.02, -60.37, FLR, 10.5))
    # field floor south of the bay, full length to the south wall
    parts.append(box(xa, xb, BAY["ys"], 79.70, -2.65, FLR))
    # south wall segment (straightened)
    parts.append(box(xa, xb, 79.70, 81.70, -2.65, 10.90))
    # Main H1 boss at (0, 9.27), top = Main underside 4.70
    parts.append(cyl(0.0, 9.27, 4.0, FLR, 4.70))
    # east south fin slice X 7..13 (fin centre (15,-8.37))
    parts.append(box(7.0, xb, -8.37, -6.72, FLR, 10.5))
    # slide-switch mounting pad on the south wall inner face, centred X 0
    # (Stage B's E-wall site is under the Wing tab; see case-3d.md):
    # pad 1.0 proud of the face (Y -3.37..-2.37), Z 2.2..8.8
    parts.append(box(-4.5, 4.5, -3.37, -2.37, 2.2, 8.8))
    return report("infill", fuse(*parts))

infill = build_infill()
# tray-left also carries the west slice of the north fin (X -8..-6):
tray_l = report("tray-left+fin", fuse(tray_l, box(-8.0, -6.0, -62.02, -60.37, FLR, 10.5)))
# (south fins are completed inside build_tray / build_infill slices)

# ================================================================ SHELL-CENTRAL
def build_shell():
    s = load("shell-central", dx=0.0)
    # cut the bay column
    s = cut(s, box(-BAY["x"], BAY["x"], BAY["yn"], BAY["ys"], 0.0, 30.0))
    # SW1 plunger hole: vertical Ø3 at (-15.5, +64.50)
    s = cut(s, cyl(-15.5, 64.50, 1.5, 5.0, 20.0))
    # DLED light-pipe hole: vertical Ø2.1 at (-4.0, +13.00)
    s = cut(s, cyl(-4.0, 13.00, 1.05, 5.0, 22.0))
    # trackpad seat: Ø44.6 recess, floor Z 11.10 (pad bottom 11.20)
    s = cut(s, cyl(0.0, 48.0, 22.3, 11.10, 23.0))
    return report("shell-central", s)

shell = build_shell()

# ================================================================ STRIPS
def build_strip(side):
    sgn = 1 if side > 0 else -1
    s = load(f"strip-{'right' if sgn>0 else 'left'}", dx=9.5 * sgn)
    s = cut(s, box(-BAY["x"], BAY["x"], BAY["yn"], BAY["ys"], 0.0, 30.0))
    return report(f"strip-{'right' if sgn>0 else 'left'}", s)

strip_r = build_strip(+1)
strip_l = build_strip(-1)

# ================================================================ PLATES
def build_plate(side):
    sgn = 1 if side > 0 else -1
    p = load(f"plate-{'right' if sgn>0 else 'left'}", dx=9.5 * sgn)
    # tip notch: half-space clip at |X| = 22.47 (as drawn in v2)
    if sgn > 0:
        p = cut(p, box(-60.0, 22.47, -80.0, 90.0, 0.0, 20.0))
    else:
        p = cut(p, box(-22.47, 60.0, -80.0, 90.0, 0.0, 20.0))
    return report(f"plate-{'right' if sgn>0 else 'left'}", p)

plate_r = build_plate(+1)
plate_l = build_plate(-1)

# ================================================================ COVER
def build_cover():
    parts = []
    # lid plate over walls: X +-30.25, Y -64.37..-0.37, top 16.65 / underside 15.15
    parts.append(box(-BAY["x"], BAY["x"], BAY["yn"], BAY["ys"], 15.15, 16.65))
    # E/W skirts: bottom 11.15 (plate top 10.90 + 0.25) — the plate tips,
    # Wing tabs and Fly all pass under the skirt line; the side closure is
    # wall + plate + skirt in sandwich (see case-3d.md).
    for sgn in (+1, -1):
        wx0, wx1 = (CAV["x"], BAY["x"]) if sgn > 0 else (-BAY["x"], -CAV["x"])
        parts.append(box(wx0, wx1, CAV["yn"], BAY["ys"], 11.15, 15.15))
        # south skirts over the 4.45 S-wall sill spans (|X| 10.90..28.25)
        q0, q1 = (10.90, CAV["x"]) if sgn > 0 else (-CAV["x"], -10.90)
        parts.append(box(q0, q1, CAV["ys"], BAY["ys"], 11.15, 15.15))
    # north skirt over the capped (7.80) middle span of the north wall
    parts.append(box(-7.50, 7.50, BAY["yn"], CAV["yn"], 7.80, 15.15))
    c = fuse(*parts)
    # cover screw holes over the north wall pilots (±24.25, -63.37)
    c = cut(c, cyl(24.25, -63.37, 1.5, 14.0, 17.0), cyl(-24.25, -63.37, 1.5, 14.0, 17.0))
    return report("cover", c)

cover = build_cover()

# ================================================================ SMALL PARTS
# SW1 plunger pin: Ø2.9 stem + Ø5 head; length set from shell column at
# (-15.5, 64.50): shell material Z 8.9..12.6 (measured) -> pin spans
# switch top (~7.4) to above shell top; head rests on shell top.
plunger = fuse(cyl(-15.5, 64.50, 1.45, 7.2, 12.9),
               cyl(-15.5, 64.50, 2.5, 12.9, 14.1))
report("plunger", plunger)
# DLED light pipe: Ø2 rod from above the LED (Main top 5.90) to the
# shell top surface at (-4, 13) (measured top 19.55; rod proud-cut at 20.5
# is trimmed in verification note; here: to 19.55).
pipe = cyl(-4.0, 13.00, 1.0, 6.4, 19.55)
report("light-pipe", pipe)

# ================================================================ FLY POCKET (tray-right)
# Decision (measured): shift Fly 1.8 north -> centre (38, -51.94);
# mouth lands 0.16 proud of the wall outer face (-56.04 at X=38).
# Pocket cut into tray-right + USB-C opening through the wall.
pocket = box(38 - 13.3, 38 + 13.3, -56.6, -47.6, 2.9, 10.0)
usb_open = box(38 - 4.6, 38 + 4.6, -57.5, -54.0, 6.1, 9.5)
tray_r = report("tray-right+fly", cut(tray_r, pocket, usb_open))
# plate-right USB rim notch: raise underside over the USB shell footprint
# (Y extended to -48.5: the Fly top sliver reaches Y -49.01, measured)
plate_r = report("plate-right+notch",
                 cut(plate_r, box(38 - 6.0, 38 + 6.0, -57.5, -48.5, 9.40, 9.78)))

# ================================================================ EXPORTS
parts = {
    "tray-left": tray_l, "tray-right": tray_r, "centre-infill": infill,
    "shell-central": shell, "strip-left": strip_l, "strip-right": strip_r,
    "plate-left": plate_l, "plate-right": plate_r, "battery-cover": cover,
    "plunger-sw1": plunger, "light-pipe-dled": pipe,
}
for name, s in parts.items():
    bd.export_step(s, f"{OUT}/{name}.step")
    bd.export_stl(s, f"{OUT}/{name}.stl")
    bd.export_brep(s, f"{ASM}/{name}.brep")
print("exported", len(parts), "parts to", OUT)
json.dump({"fly_centre": [38, -51.94]}, open(f"{ASM}/params.json", "w"))
