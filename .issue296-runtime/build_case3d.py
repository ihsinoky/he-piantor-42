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
RT = "/home/hatch/workspace/projects/he-piantor-case296b/.issue296-runtime"
CAPS = json.load(open(RT + "/caps.json"))   # keycap envelopes (extract_caps.py)
FLUSH_Y = -64.37                            # north outline limit (Stage B)

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
        # --- (removed 2026-11-21) the Stage-3D cover screw pilot at
        # (sgn*24.25, -63.37) is superseded by the shelf fixing: the
        # axis sits 1.00 from the flush face, so no standard screw
        # head fits inside the outline there. See SHELF FIXING.
    # --- south dent wall removal + straightening fill (this half's slice)
    sx0, sx1 = max(-50.0, xa), min(50.0, xb)
    if sx1 > sx0:
        t = cut(t, box(sx0, sx1, 68.4, 70.6, FLR, 11.0))          # old dent wall
        t = fuse(t, box(sx0, sx1, 70.0, 79.70, -2.65, FLR))       # band floor
        t = fuse(t, box(sx0, sx1, 79.70, 81.70, -2.65, 10.90))    # new south wall
    return report(f"tray-{'right' if sgn>0 else 'left'}", t)

tray_r = build_tray(+1)
tray_l = build_tray(-1)

# ================================================================ NORTH FLUSH FILL
# PO 2026-11-21: the north face must be flush (tsuraichi) at the outline
# limit Y = -64.37. The g17 tray north face is vertical but traces a plan
# arc (sag up to ~8.9 mm at |X| ~32, meeting the plane at |X| ~118;
# measured in measure_north4.py). Fill the tray face forward to the
# plane, Z -2.65..10.90, in 2 mm columns hugging the measured face
# (+0.30 embed). Columns on the angled end edge (|centre| > 117) and
# zero-sag columns (bay wall) are left alone.
def north_fill(t):
    fills = []
    for xi in range(-120, 120, 2):
        if abs(xi + 1) > 117:
            continue
        cells = t.intersect(box(xi, xi + 2, -70, -30, -2.65, 10.90))
        cells = list(cells) if isinstance(cells, (list, bd.ShapeList)) else [cells]
        cells = [c for c in cells if c is not None and c.volume > 1e-6]
        if not cells:
            continue
        face = min(c.bounding_box().min.Y for c in cells)
        if face - FLUSH_Y > 0.05:
            fills.append(box(xi, xi + 2, FLUSH_Y, face + 0.30, -2.65, 10.90))
    if fills:
        t = fuse(t, *fills)
    return t

tray_r = report("tray-right+flush", north_fill(tray_r))
tray_l = report("tray-left+flush", north_fill(tray_l))

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
def build_strip_old(side):
    sgn = 1 if side > 0 else -1
    s = load(f"strip-{'right' if sgn>0 else 'left'}", dx=9.5 * sgn)
    s = cut(s, box(-BAY["x"], BAY["x"], BAY["yn"], BAY["ys"], 0.0, 30.0))
    return report(f"strip-old-{'right' if sgn>0 else 'left'}", s)

strip_r_old = build_strip_old(+1)
strip_l_old = build_strip_old(-1)

# ================================================================ NORTH BAND (PO profile 2026-11-21)
# The strips are REPLACED by band plateaus: top at the keytop datum
# 22.00, from the flush north face south to just before the keys.
# South edge per 1 mm column = keycap capline (caps.json, 16.5 mm cap
# envelopes at each key's own angle) - 1.0 mm clearance; cap-free
# columns take the nearest cap column's line. Z 10.90..22.00 (bottom =
# plate top). North edge: the flush plane for |X| <= 116; beyond, the
# tray's own outline sampled at the column's outer sub-column (no
# overhang past the angled end edge).
def build_plateau(tray, side):
    sgn = 1 if side > 0 else -1
    caps = CAPS["right" if sgn > 0 else "left"]["capline"]
    capcols = sorted(int(k) for k in caps)
    def south_edge(xa, xb):
        ks = [k for k in range(int(xa // 1), int(xb // 1) + 1) if str(k) in caps]
        if ks:
            return min(caps[str(k)] for k in ks) - 1.0
        near = min(capcols, key=lambda c: abs(c - (xa + xb) / 2))
        return caps[str(near)] - 1.0
    boxes = []
    e = 30.25
    while e < 154.5:
        xa, xb = (e, e + 1.0) if sgn > 0 else (-e - 1.0, -e)
        if sgn < 0:
            xa, xb = -e - 1.0, -e
        if abs((xa + xb) / 2) <= 116:
            yn = FLUSH_Y
        else:
            # sample the tray outline over the outer half of the column
            sxa = xb - 0.5 if sgn > 0 else xa
            cells = tray.intersect(box(sxa, sxa + 0.5, -70, 90, -2.65, 10.90))
            cells = list(cells) if isinstance(cells, (list, bd.ShapeList)) else [cells]
            cells = [c for c in cells if c is not None and c.volume > 1e-6]
            if not cells:
                e += 1.0
                continue
            yn = min(c.bounding_box().min.Y for c in cells)
        ys = south_edge(xa, xb)
        if ys - yn >= 1.0:
            boxes.append(box(xa, xb, yn, ys, 10.90, 22.00))
        e += 1.0
    p = fuse(*boxes)
    # shelf fixing (PO lid-integral decision 2026-11-21): flat-head
    # M3 at (sgn*55, -61.37) and (sgn*85, -61.37) — through hole
    # O3.0 + 90-deg countersink (head O5.5 x 1.25, top flush at
    # 22.00; head rim at Y -64.12, 0.25 inside the flush face).
    for sx in (55.0, 85.0):
        cx = sgn * sx
        p = cut(p, cyl(cx, -61.37, 1.5, 10.40, 22.50))
        p = cut(p, bd.Solid.make_cone(1.5, 2.75, 1.25,
                                      bd.Plane(origin=(cx, -61.37, 20.75))))
    return report(f"strip-{'right' if sgn>0 else 'left'} (band)", p)

strip_r = build_plateau(tray_r, +1)
strip_l = build_plateau(tray_l, -1)

# ================================================================ SHELL REVISION (PO profile)
# Centre + south go to plate height 10.90 with a slope transition from
# the band: profile (Y,Z) — 22.00 at the bay south wall face (-0.37),
# linear to 10.90 at Y 20.0, flat 10.90 south of it. Applied as a
# Y-Z profile cut over X +-41.5 to shell-central fused with the old
# strips' south lobes (transferred here). Trackpad island exempted
# (D-053: keep-disc r 23.5 at (0,48)). DLED hole re-cut afterwards
# (the slope fuse/cut crosses it); the SW1 hole survives the top cut.
def as_solid(sh):
    if isinstance(sh, (list, bd.ShapeList)):
        ss = [s for s in sh if s is not None and hasattr(s, "volume") and s.volume > 1e-6]
        return fuse(*ss) if ss else None
    return sh

lobe_r = as_solid(strip_r_old.intersect(box(10.0, 30.25, -0.37, 30.0, 0.0, 23.0)))
lobe_l = as_solid(strip_l_old.intersect(box(-30.25, -10.0, -0.37, 30.0, 0.0, 23.0)))
for lb in (lobe_r, lobe_l):
    if lb is not None:
        shell = fuse(shell, lb)
prof_pts = [(0, -0.37, 22.00), (0, 20.0, 10.90), (0, 95.0, 10.90),
            (0, 95.0, 23.5), (0, -0.37, 23.5)]
prof_wire = bd.Wire.make_polygon([bd.Vector(*p) for p in prof_pts] +
                                 [bd.Vector(*prof_pts[0])])
prof_face = bd.Face(prof_wire)
prof_cut = bd.extrude(prof_face, 83.0)
_pbb = prof_cut.bounding_box()
prof_cut = prof_cut.moved(bd.Location((-41.5 - _pbb.min.X, 0, 0)))
prof_cut = prof_cut.cut(cyl(0.0, 48.0, 23.5, 0.0, 23.5))
shell_pre = shell
shell = cut(shell, prof_cut)

# SLOPE SHEET (successor fix, 2026-11-21): the profile cut alone
# deletes the centre skin wherever its underside (~2.1 under the old
# ridge top) sits above the new profile — measured hole along the
# spine |X| <= ~9, Y 6..27, plus the apron widening Y 21..30 and the
# lobe bands (diag_grid.py vs the Stage-3D shell). Add a sheet whose
# top IS the profile (2.0 thick), limited to the pre-cut shell's plan
# footprint (its downward sweep), so the slope surface exists.
# Zone A |X| <= 22.4 (spine + apron; plate-free). Zone B: the lobe
# bands 22.4 < |X| <= 30.25, sheet floored at the plate top 10.90
# (it lands on the plate field, never inside it).
low_pts = [(0, -0.37, 20.00), (0, 20.0, 8.90), (0, 95.0, 8.90),
           (0, 95.0, 23.5), (0, -0.37, 23.5)]
low_wire = bd.Wire.make_polygon([bd.Vector(*p) for p in low_pts] +
                                [bd.Vector(*low_pts[0])])
slab_low = bd.extrude(bd.Face(low_wire), 83.0)
_lbb = slab_low.bounding_box()
slab_low = slab_low.moved(bd.Location((-41.5 - _lbb.min.X, 0, 0)))
slab_low = slab_low.cut(cyl(0.0, 48.0, 23.5, 0.0, 23.5))

def sweep_down(src, steps=14):
    r = src
    for dz in range(1, steps + 1):
        r = fuse(r, src.moved(bd.Location((0, 0, -float(dz)))))
    return r

def sheet_from(src):
    if src is None:
        return None
    sh = as_solid(sweep_down(src).intersect(slab_low))
    if sh is not None:
        sh = as_solid(sh.cut(prof_cut))
    return sh

zone_a = as_solid(shell_pre.intersect(box(-22.4, 22.4, -0.37, 40.0, 0.0, 23.0)))
sheet_a = sheet_from(zone_a)
if sheet_a is not None:
    shell = fuse(shell, sheet_a)
for sgn in (+1, -1):
    zb = box(22.4, 30.25, -0.37, 30.0, 0.0, 23.0) if sgn > 0 else \
        box(-30.25, -22.4, -0.37, 30.0, 0.0, 23.0)
    sheet_b = sheet_from(as_solid(shell_pre.intersect(zb)))
    if sheet_b is not None:
        sheet_b = as_solid(sheet_b.intersect(
            box(-31.0, 31.0, -1.0, 31.0, 10.90, 23.5)))
    if sheet_b is not None:
        shell = fuse(shell, sheet_b)

# SW1 boss cap: the trackpad keep-disc (r 23.5 at (0,48)) also
# exempts the SW1 boss (centre distance 22.6) from the profile cut,
# leaving its top at the pre-revision 11.10 (measured); the
# re-trimmed plunger rests on a 10.90 surface -> cap the boss.
shell = cut(shell, box(-19.0, -12.0, 60.0, 69.0, 10.90, 23.5))
shell = cut(shell, cyl(-4.0, 13.00, 1.05, 5.0, 23.0))   # DLED hole re-cut
shell = report("shell-central rev", shell)

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
    # lid plate over walls: X +-30.25, Y -64.37..-0.37.
    # PO profile 2026-11-21: lid top raised to the keytop datum 22.00
    # (was 16.65) so the north band is continuous over the bay;
    # underside stays 15.15 (cell clearance unchanged).
    parts.append(box(-BAY["x"], BAY["x"], BAY["yn"], BAY["ys"], 15.15, 22.00))
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
    # No screw holes in the lid portion: in the shelf design the
    # fixing lives in the plateaus (see build_plateau); the Stage-3D
    # centre pair at (±24.25, -63.37) is removed — no standard head
    # fits 1.00 from the flush face.
    return report("cover", c)

cover = build_cover()

# ================================================================ SMALL PARTS
# SW1 plunger pin: Ø2.9 stem + Ø5 head. PO profile: the shell top at
# (-15.5, 64.50) is now the plate-height field 10.90 (was ~12.6), so
# the pin is re-trimmed: stem 7.2..10.9 (bottom still 1.3 above the
# Main top 5.90, over the future tact switch ~7.4), head 10.9..12.1
# resting on the 10.90 surface.
plunger = fuse(cyl(-15.5, 64.50, 1.45, 7.2, 10.9),
               cyl(-15.5, 64.50, 2.5, 10.9, 12.1))
report("plunger", plunger)
# DLED light pipe: Ø2 rod from above the LED (Main top 5.90) to the
# shell surface at (-4, 13) — now the centre slope: profile Z at
# Y=13 is 22 - (13.37)*(11.10/20.37) = 14.71.
pipe = cyl(-4.0, 13.00, 1.0, 6.4, 14.71)
report("light-pipe", pipe)

# ================================================================ FLY POCKET (tray-right)
# Stage 3D decision: shift Fly 1.8 north -> centre (38, -51.94), mouth
# 0.16 proud of the (then arc) wall face. PO north-flush revision
# 2026-11-21: the face at X=38 moves to the plane -64.37, so the Fly
# shifts a further ~8.06 north -> centre (38, -60.00) and the mouth
# lands exactly flush with the new face (0.00 proud; 0.16 proud is
# impossible at the outline limit). The first pass used centre
# -60.11 from a wall-face datum and measured +0.11 proud on the
# fused official body; corrected by the measured mouth position.
# EZmate route ~96.7 mm total, still << the 170 mm stock cable.
# Pocket cut into tray-right + USB-C opening through the (now
# filled) wall; both shift with it.
pocket = box(38 - 13.3, 38 + 13.3, -64.66, -55.66, 2.9, 10.0)
usb_open = box(38 - 4.6, 38 + 4.6, -65.56, -62.06, 6.1, 9.5)
tray_r = report("tray-right+fly", cut(tray_r, pocket, usb_open))
# plate-right USB rim notch: raise underside over the USB shell footprint
# (Y extended to -56.56: the Fly top sliver, at Y -49.01 in the old
# pose, reaches Y -57.07 at the new pose)
plate_r = report("plate-right+notch",
                 cut(plate_r, box(38 - 6.0, 38 + 6.0, -65.56, -56.56, 9.40, 9.78)))

# ================================================================ SHELF FIXING (tray pilots)
# Pilots for the shelf's flat-head M3 screws: O2.7 into the tray
# north fill at (±55, -61.37) and (±85, -61.37), Z 4.0..10.90
# (pilot fill fraction 100% measured — diag_shelf2.py; the fill is
# solid there and the shaft cylinders clear Wings/plates by 0.000).
for sx in (55.0, 85.0):
    tray_r = cut(tray_r, cyl(sx, -61.37, 1.35, 4.0, 10.90))
    tray_l = cut(tray_l, cyl(-sx, -61.37, 1.35, 4.0, 10.90))
tray_r = report("tray-right+pilots", tray_r)
tray_l = report("tray-left+pilots", tray_l)

# ================================================================ EXPORTS
# PO 2026-11-21: the lid is INTEGRAL with the north band — one
# removable north shelf; battery swap = remove the shelf, swap
# cells, refit. Replaces battery-cover + strip-left + strip-right
# (11 -> 9 parts). The shell keeps the centre slope; the shelf's
# centre south edge (Y -0.37) meets the slope's top edge.
shelf = report("north-shelf", fuse(cover, strip_l, strip_r))
parts = {
    "tray-left": tray_l, "tray-right": tray_r, "centre-infill": infill,
    "shell-central": shell, "north-shelf": shelf,
    "plate-left": plate_l, "plate-right": plate_r,
    "plunger-sw1": plunger, "light-pipe-dled": pipe,
}
for name, s in parts.items():
    bd.export_step(s, f"{OUT}/{name}.step")
    bd.export_stl(s, f"{OUT}/{name}.stl")
    bd.export_brep(s, f"{ASM}/{name}.brep")
print("exported", len(parts), "parts to", OUT)
json.dump({"fly_centre": [38, -60.00]}, open(f"{ASM}/params.json", "w"))
