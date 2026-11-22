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
# P0/P1 revision (Opus review, PO 2026-11-21): the south edge is no
# longer the 1.0 mm staircase (true min gap was 0.571). Boxes now
# extend to capline - 0.05 and are trimmed by per-cap DISC-OFFSET
# keep-out prisms (radius GAP below), so the edge is the true
# offset curve of the cap rectangles — uniform perpendicular gap.
# GAP = 1.30 nominal from the P0-1 tolerance stack-up (worst-case
# sum 0.95 -> residual +0.35; see case-3d.md addendum). Cap-free
# columns take the nearest cap column's line. Z 11.10..22.00
# (underside raised 0.20 = the P1 mating gap over plate/tray top
# 10.90). North edge: the flush plane for |X| <= 116; beyond, the
# tray's own outline sampled at the column's outer sub-column (no
# overhang past the angled end edge).
GAP = 1.30

def prism2d(pts, z0, z1):
    """Vertical prism of a 2D polygon loop (points re-ordered CCW
    so bd.extrude goes +Z), spanning Z z0..z1."""
    area = 0.0
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        area += x0 * y1 - x1 * y0
    if area < 0:
        pts = pts[::-1]
    w = bd.Wire.make_polygon([bd.Vector(x, y, 0) for (x, y) in pts] +
                             [bd.Vector(*pts[0], 0)])
    s = bd.extrude(bd.Face(w), z1 - z0)
    return s.moved(bd.Location((0, 0, z0)))

def cap_keepout(poly, g, z0, z1):
    """Disc-offset (Minkowski with radius g) prism of one cap
    polygon: base prism + one outward quad per edge + one cylinder
    per vertex. Exact for convex polygons (caps are rectangles)."""
    pts = [(p[0], p[1]) for p in poly]
    n = len(pts)
    cen = (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n)
    solids = [prism2d(pts, z0, z1)]
    for i in range(n):
        ax, ay = pts[i]
        bx, by = pts[(i + 1) % n]
        ex, ey = bx - ax, by - ay
        ln = (ex * ex + ey * ey) ** 0.5
        nx, ny = ey / ln, -ex / ln
        mx, my = (ax + bx) / 2 + nx, (ay + by) / 2 + ny
        if (mx - cen[0]) ** 2 + (my - cen[1]) ** 2 < \
           ((ax + bx) / 2 - cen[0]) ** 2 + ((ay + by) / 2 - cen[1]) ** 2:
            nx, ny = -nx, -ny
        quad = [(ax, ay), (bx, by), (bx + g * nx, by + g * ny),
                (ax + g * nx, ay + g * ny)]
        solids.append(prism2d(quad, z0, z1))
        solids.append(cyl(ax, ay, g, z0, z1))
    return fuse(*solids)

def build_plateau(tray, side):
    sgn = 1 if side > 0 else -1
    caps = CAPS["right" if sgn > 0 else "left"]["capline"]
    capcols = sorted(int(k) for k in caps)
    def south_edge(xa, xb):
        ks = [k for k in range(int(xa // 1), int(xb // 1) + 1) if str(k) in caps]
        if ks:
            return min(caps[str(k)] for k in ks) - 0.05
        near = min(capcols, key=lambda c: abs(c - (xa + xb) / 2))
        return caps[str(near)] - 0.05
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
            boxes.append(box(xa, xb, yn, ys, 11.10, 22.00))
        e += 1.0
    p = fuse(*boxes)
    # trim by the per-cap offset keep-outs (only caps whose offset
    # bbox can reach the plateau)
    pbb = p.bounding_box()
    for poly in CAPS["right" if sgn > 0 else "left"]["cap_polys"]:
        xs = [q[0] for q in poly]
        ys = [q[1] for q in poly]
        if max(xs) + GAP < pbb.min.X or min(xs) - GAP > pbb.max.X:
            continue
        if max(ys) + GAP < pbb.min.Y or min(ys) - GAP > pbb.max.Y:
            continue
        p = cut(p, cap_keepout(poly, GAP, 10.5, 22.5))
    # (A) hinge round (PO 2026-11-22): the P0/P1 screw fixing is
    # ABOLISHED — no screw holes, no countersinks, no pry notches.
    # The shelf is held by the central south-edge hinge + ONE
    # slide latch. The latch's first seat was on THIS plateau
    # (slider groove X 67.7..96.3, centring dip, stem web slot,
    # receiver in tray-right at X +85); the trim round abolished
    # that seat and relocated the latch to the bay north rib at
    # X +12 (LATCH, RELOCATED below). CORRECTION round: the band
    # is restored but the X+85 seat is NOT — the plateau is the
    # plain P0/P1 band, no groove, no dip, no slot.
    return report(f"strip-{'right' if sgn>0 else 'left'} (band)", p)

# CORRECTION round (PO 2026-11-22): the band plateaus ARE built
# again. The trim round cut the shelf back to the cover alone —
# an overshoot (PMO misread the PO's trim instruction): the PO
# wanted only the shelf portions at the far east/west ENDS of
# the keyboard removed, i.e. beyond the outermost keys; the band
# over the Wing key fields stays, reaching close to the keys.
# Shelf end (probe_corr.py, from caps.json cap_polys + the
# pre-trim shelf at 99478610a): the outermost keycap extent is
# |X| = 151.001 (the outer Wing cap's east/west corner, both
# sides symmetric); the pre-trim shelf ran to +-153.25. The end
# is set at the outermost cap extent + 1.30 — the project's own
# cap-gap rule applied at the end face — X_END = 152.30, a clean
# vertical face. The strips are clipped there; the cover
# (|X| <= 30.25) is unaffected.
SHELF_END = 152.30
strip_r = cut(build_plateau(tray_r, +1),
              box(SHELF_END, 200.0, -70.0, 90.0, 0.0, 30.0))
strip_r = report("strip-right+endclip", strip_r)
strip_l = cut(build_plateau(tray_l, -1),
              box(-200.0, -SHELF_END, -70.0, 90.0, 0.0, 30.0))
strip_l = report("strip-left+endclip", strip_l)

# ================================================================ SHELL REVISION (PO profile)
# Centre + south go to plate height 10.90. (B) PO 2026-11-22: the
# centre slope is REMOVED ("the slope is needless complexity") —
# the profile is a STEP: flat 10.90 for all Y >= -0.37 (the shell
# steps straight down from the shelf's south edge). Applied as a
# Y-Z profile cut over X +-41.5 to shell-central fused with the old
# strips' south lobes (transferred here). Trackpad island exempted
# (D-053: keep-disc r 23.5 at (0,48)). DLED hole re-cut afterwards;
# the SW1 hole survives the top cut. (Supersedes the 2026-11-21
# slope element of the PO profile; the cliff was the PO's allowed
# fallback in the original text and is now the design.)
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
prof_pts = [(0, -0.37, 10.90), (0, 95.0, 10.90),
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

# FLAT SHEET (was SLOPE SHEET, 2026-11-21; flattened by (B)
# 2026-11-22): the profile cut alone deletes the centre skin
# wherever its underside sits above 10.90 — the same spine/apron/
# lobe zones measured for the slope. Add a flat sheet whose top IS
# the new profile (Z 8.90..10.90, 2.0 thick), limited to the
# pre-cut shell's plan footprint (its downward sweep), so the
# 10.90 surface exists everywhere the cut removed it.
# Zone A |X| <= 22.4 (spine + apron; plate-free). Zone B: the lobe
# bands 22.4 < |X| <= 30.25, sheet floored at the plate top 10.90
# (zero thickness under the flat profile -> no sheet there).
low_pts = [(0, -0.37, 8.90), (0, 95.0, 8.90),
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
    # lid plate over walls: X +-30.25, Y -64.37..-0.57.
    # PO profile 2026-11-21: lid top raised to the keytop datum 22.00
    # (was 16.65) so the north band is continuous over the bay.
    # P1 mating gaps (Opus review): underside 15.15 -> 15.35 (0.20
    # over the wall tops 15.15) and the south edge -0.37 -> -0.57
    # (0.20 from the shell slope's top edge).
    parts.append(box(-BAY["x"], BAY["x"], BAY["yn"], -0.57, 15.35, 22.00))
    # E/W skirts: bottom 11.15 (plate top 10.90 + 0.25) — the plate tips,
    # Wing tabs and Fly all pass under the skirt line; the side closure is
    # wall + plate + skirt in sandwich (see case-3d.md). Tops extended
    # to the raised lid underside 15.35; south ends follow the lid
    # edge -0.57.
    for sgn in (+1, -1):
        wx0, wx1 = (CAV["x"], BAY["x"]) if sgn > 0 else (-BAY["x"], -CAV["x"])
        parts.append(box(wx0, wx1, CAV["yn"], -0.57, 11.15, 15.35))
        # south skirts over the 4.45 S-wall sill spans (|X| 10.90..28.25)
        q0, q1 = (10.90, CAV["x"]) if sgn > 0 else (-CAV["x"], -10.90)
        parts.append(box(q0, q1, CAV["ys"], -0.57, 11.15, 15.35))
    # north skirt over the capped (7.80) middle span of the north wall;
    # bottom raised to 8.00 = 0.20 mating gap over the wall top 7.80
    parts.append(box(-7.50, 7.50, BAY["yn"], CAV["yn"], 8.00, 15.35))
    c = fuse(*parts)
    # No screw holes in the lid portion: in the shelf design the
    # fixing lives in the plateaus (see build_plateau); the Stage-3D
    # centre pair at (±24.25, -63.37) is removed — no standard head
    # fits 1.00 from the flush face.
    return report("cover", c)

cover = build_cover()

# ================================================================ SMALL PARTS
# SW1 plunger pin: Ø2.9 stem + Ø4 head (P1: head Ø5 -> Ø4, plan
# clearance to the real Ø40 trackpad module 0.14 -> 0.64). PO
# profile: the shell top at (-15.5, 64.50) is now the plate-height
# field 10.90 (was ~12.6), so the pin is re-trimmed: stem 7.2..10.9
# (bottom still 1.3 above the Main top 5.90, over the future tact
# switch ~7.4), head 10.9..12.1 resting on the 10.90 surface.
plunger = fuse(cyl(-15.5, 64.50, 1.45, 7.2, 10.9),
               cyl(-15.5, 64.50, 2.0, 10.9, 12.1))
report("plunger", plunger)
# DLED light pipe: Ø2 rod from above the LED (Main top 5.90) to the
# shell surface at (-4, 13) — (B) 2026-11-22: the slope is gone,
# the surface there is the flat 10.90 field; pipe re-trimmed from
# 14.71 to 10.90.
pipe = cyl(-4.0, 13.00, 1.0, 6.4, 10.90)
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

# ================================================================ SHELF FIXING (tray inserts)
# P1 (Opus review): the Ø2.7 self-tap pilots are replaced by
# heat-set inserts on the moved row Y -60.37 (P0-2). Insert holes
# O4.2, Z 5.0..10.90 (depth 5.9) for M3 x 5.7-class inserts, top
# flush with the tray top 10.90. Pre-change measurement
# (diag_p0p1.py, pilot void restored): at (±55, -60.37) the hole
# is 100% in tray material, min wall >= 1.50/1.75, floor solid —
# no boss needed. At (±85, -60.37) a 0.207 mm3 sliver of the hole's
# top south rim (Z 9.40..10.90) opens into the tray's plate-seat
# step, so a boss cylinder r4.6 (Z 4.0..10.90) is fused in first,
# trimmed by the plate solid (the plate edge backs the rim there);
# boss min wall around the hole = 2.5 by construction.
# the boss is trimmed to the flush plane: its raw cylinder would
# reach Y -64.97, 0.60 proud of the north face. It is also trimmed
# by the Wing bodies: the board's north corner sits in a tray
# recess at (85, -56.1, Z 4.70..5.90) and the raw boss filled
# 0.611 mm3 of that recess (found by verify_p0p1 section G,
# fixed here — the trim leaves >= 1.92 of boss wall south of the
# hole in the board's Z band).
_wings_b = fuse(load("wing_right", dx=9.5), load("wing_left", dx=-9.5),
                *[load(e["name"], dx=-9.5)
                  for e in idx if e["name"].startswith("underside-left")],
                *[load(e["name"], dx=9.5)
                  for e in idx if e["name"].startswith("underside-right")])
boss_r = cut(cyl(85.0, -60.37, 4.6, 4.0, 10.90),
             box(60.0, 110.0, -70.0, FLUSH_Y, 3.0, 11.5), _wings_b)
boss_l = cut(cyl(-85.0, -60.37, 4.6, 4.0, 10.90),
             box(-110.0, -60.0, -70.0, FLUSH_Y, 3.0, 11.5), _wings_b)
tray_r = fuse(tray_r, boss_r)
tray_r = cut(tray_r, plate_r)
tray_l = fuse(tray_l, boss_l)
tray_l = cut(tray_l, plate_l)
# (A) hinge round: the four heat-set insert holes are ABOLISHED
# with the screw fixing — the bosses stay as plain geometry.
# TRIM round: +85 hosted the latch receiver in the hinge round;
# the latch moved to the bay north rib (LATCH, RELOCATED below)
# and the +85 boss is plain again, like -85.
tray_r = report("tray-right+bosses", tray_r)
tray_l = report("tray-left+bosses", tray_l)

# ================================================================ SOUTH UNIFICATION (plan A, PO 2026-11-22)
# Opus proposal files/case296-south-unify-opus-2026-11-22.md §3,
# adopted by the PO. All measured inputs are re-derived here from
# the built solids (the north_fill pattern): tray south face C(X),
# plate south profile, shell south face. Constants of record:
#   Y_S = 81.700 (81.702 abolished), R = 4.0 arc, skin Z 9.30..10.90,
#   shell edge 69.700, band north boundary B(X) per §3-2.
# Diagonal fitted by least squares on the tray face samples
# |X| 61..70 (probe: Y = 128.49 - 0.784|X|, resid <= 0.018);
# intersection / tangent points recomputed from the fit per §3-1's
# own instruction. Probe values: Xi 59.68, Xt1 58.30, Xt2 60.77.
import math

YS = 81.700
R_ARC = 4.0

def _cells(r):
    if r is None:
        return []
    items = list(r) if isinstance(r, (list, bd.ShapeList)) else [r]
    return [c for c in items if c is not None and hasattr(c, "volume")
            and c.volume > 1e-9]

def southmost(solid, xa, xb, z0, z1, y0=40.0, y1=95.0):
    cs = _cells(solid.intersect(box(xa, xb, y0, y1, z0, z1)))
    return max((c.bounding_box().max.Y for c in cs), default=None)

def sample_face(solid, sgn, x_from, x_to, z0, z1, y0=40.0, y1=95.0):
    """{|X| station centre (0.5 grid, offset .25): southmost Y},
    sampled in the columns at sgn * |X|."""
    out = {}
    k = int(round((x_from - 0.25) / 0.5))
    while True:
        xc = 0.25 + 0.5 * k
        if xc > x_to:
            break
        xa, xb = (xc - 0.25, xc + 0.25) if sgn > 0 else (-xc - 0.25, -xc + 0.25)
        out[xc] = southmost(solid, xa, xb, z0, z1, y0, y1)
        k += 1
    return out

# --- measured faces (BEFORE any south modification) ---
face_r = sample_face(tray_r, +1, 44.0, 76.0, -2.65, 10.90)
face_l = sample_face(tray_l, -1, 44.0, 76.0, -2.65, 10.90)
plate_r_s = sample_face(plate_r, +1, 40.0, 61.0, -3.0, 23.0)
plate_l_s = sample_face(plate_l, -1, 40.0, 61.0, -3.0, 23.0)
shell_f = {}
for sgn in (+1, -1):
    for xc, v in sample_face(shell, sgn, 0.0, 41.5, -3.0, 23.0,
                             55.0, 75.0).items():
        shell_f[sgn * xc] = v

# --- diagonal fit + arc constants (right tray; L/R faces identical) ---
_fp = [(x, c) for x, c in face_r.items() if 61.0 <= x <= 70.0 and c is not None]
_n = len(_fp)
_sx = sum(p[0] for p in _fp); _sy = sum(p[1] for p in _fp)
_sxx = sum(p[0] ** 2 for p in _fp); _sxy = sum(p[0] * p[1] for p in _fp)
MD = (_n * _sxy - _sx * _sy) / (_n * _sxx - _sx ** 2)     # slope (< 0)
AD = (_sy - MD * _sx) / _n                                 # intercept
XI = (YS - AD) / MD                                        # line meets Y_S
TH = math.atan(-MD)
TL = R_ARC * math.tan(TH / 2.0)                            # tangent length
XT1 = XI - TL                                              # tangent pt, straight
CY = YS - R_ARC                                            # arc centre Y
XT2 = XI + TL * math.cos(TH)                               # tangent pt, diagonal
print(f"south: diagonal Y = {AD:.4f} {MD:+.4f}|X|; Xi {XI:.3f}, "
      f"Xt1 {XT1:.3f}, Xt2 {XT2:.3f}, arc centre Y {CY:.3f}")

def S_of(x):
    """New south outline S(|X|): straight, R4 arc, then the diagonal."""
    if x <= XT1:
        return YS
    if x >= XT2:
        return AD + MD * x
    return CY + math.sqrt(max(R_ARC ** 2 - (x - XT1) ** 2, 0.0))

def outline_stations(x_from, x_to):
    """Fine |X| stations along S: 1.0 on the straight, 0.25 on the arc."""
    xs = [x_from]
    x = x_from + 1.0
    while x < min(XT1, x_to):
        xs.append(round(x, 3)); x += 1.0
    if XT1 < x_to:
        xs.append(round(XT1, 3))
        x = XT1 + 0.25
        while x < min(XT2, x_to):
            xs.append(round(x, 3)); x += 0.25
        xs.append(round(min(XT2, x_to), 3))
    else:
        xs.append(round(x_to, 3))
    return sorted(set(xs))

# --- tray outline: face-following fill + overshoot clip, per side ---
def unify_tray(t, sgn, face):
    xs = outline_stations(44.0, XT2)
    south = [(sgn * x, S_of(x)) for x in xs]
    north = []
    for xc in sorted(face, reverse=True):
        if not (44.0 <= xc <= XT2 + 0.25) or face[xc] is None:
            continue
        north.append((sgn * xc, min(face[xc], S_of(xc)) - 0.30))
    fill = prism2d(south + north, -2.65, 10.90)
    t = fuse(t, fill)
    clip = prism2d(south + [(sgn * XT2, 95.0), (sgn * 44.0, 95.0)],
                   -3.0, 11.60)
    t = cut(t, clip)
    return report(f"tray-{'right' if sgn > 0 else 'left'}+south", t)

tray_r = unify_tray(tray_r, +1, face_r)
tray_l = unify_tray(tray_l, -1, face_l)

# --- shell south edge -> one straight line at 69.700 (face fill) ---
_sh_xs = sorted(shell_f)
_sh_south = [(-41.0, 69.700), (41.0, 69.700)]
_sh_north = [(x, min(shell_f[x], 69.700) - 0.30)
             for x in reversed(_sh_xs)
             if shell_f[x] is not None and abs(x) <= 41.0]
shell = fuse(shell, prism2d(_sh_south + _sh_north, 8.90, 10.90))
shell = report("shell-central+south", shell)

# --- south band skin (Z 9.30..10.90, hollow below), per part slice ---
def B_of(x, plate_face):
    """Band north boundary B(|X|) per proposal §3-2; the plate
    profile is looked up at the nearest sampled station."""
    if x <= 41.01:
        return 70.000
    if not plate_face:
        return 70.000
    pf = plate_face[min(plate_face, key=lambda kk: abs(kk - x))]
    if pf is None:
        return 70.000
    return max(70.000, pf + 0.30)

def skin_prism(x_lo, x_hi, plate_face):
    """Skin prism over one part slice; the slice bounds are explicit
    polygon stations so the seams at the part boundaries come out
    at exactly 0.30 (bounds are set seam -/+ 0.15 by the caller)."""
    xs = {round(x_lo, 2), round(x_hi, 2)}
    k = int(math.ceil((x_lo - 0.25) / 0.5))
    while 0.25 + 0.5 * k <= x_hi:
        xs.add(round(0.25 + 0.5 * k, 2)); k += 1
    pts_n, pts_s = [], []
    for x in sorted(xs):
        b = B_of(abs(x), plate_face)
        if S_of(abs(x)) - b >= 0.5:
            pts_n.append((x, b))
            pts_s.append((x, S_of(abs(x))))
    if len(pts_n) < 2:
        return None
    return prism2d(pts_n + pts_s[::-1], 9.30, 10.90)

def plate_clearance(plate):
    """The plate's plan region dilated by exactly 0.30 (2D offset of
    its top face, extruded over the skin's Z range). The station
    chords of B(X) alone cut across the plate's step corner at
    |X| ~ 50 (first build measured a 0.043 gap there); carving the
    skin with this solid makes the joint a true 0.30 offset."""
    top = [f for f in plate.faces() if abs(f.center().Z - 10.90) < 0.01][0]
    sol = None
    for f in bd.offset(top, 0.30).faces():
        p = bd.extrude(f, 1.80).moved(bd.Location((0, 0, -1.70)))
        sol = p if sol is None else sol.fuse(p)
    return sol

_clr_r = plate_clearance(plate_r)
_clr_l = plate_clearance(plate_l)
_sk = skin_prism(-60.5, -6.15, plate_l_s)
if _sk is not None:
    tray_l = fuse(tray_l, cut(_sk, _clr_l))
_sk = skin_prism(-5.85, 12.85, plate_r_s)
if _sk is not None:
    infill = fuse(infill, _sk)
_sk = skin_prism(13.15, 60.5, plate_r_s)
if _sk is not None:
    tray_r = fuse(tray_r, cut(_sk, _clr_r))
tray_l = report("tray-left+skin", tray_l)
infill = report("infill+skin", infill)
tray_r = report("tray-right+skin", tray_r)

# --- C0.5 chamfer on the south top edge (straight + arcs) ---
_tri_pts = [bd.Vector(0, YS - 0.50, 10.90), bd.Vector(0, YS, 10.40),
            bd.Vector(0, YS, 10.90)]
_tri_w = bd.Wire.make_polygon(_tri_pts + [_tri_pts[0]])
_tri = bd.extrude(bd.Face(_tri_w), 2 * XT1)
_tri = _tri.moved(bd.Location((-XT1 - _tri.bounding_box().min.X, 0, 0)))
tray_r = cut(tray_r, _tri)
tray_l = cut(tray_l, _tri)
infill = cut(infill, _tri)

def arc_chamfer_cutter(sgn):
    cx, cy = sgn * XT1, CY
    outer = cyl(cx, cy, 6.0, 10.40, 11.60)
    keep = bd.Solid.make_cone(4.0, 2.8, 1.2,
                              bd.Plane(origin=(cx, cy, 10.40)))
    a1, a2 = (50.0, 91.0) if sgn > 0 else (89.0, 130.0)
    wp = [(cx, cy),
          (cx + 9 * math.cos(math.radians(a1)),
           cy + 9 * math.sin(math.radians(a1))),
          (cx + 9 * math.cos(math.radians(a2)),
           cy + 9 * math.sin(math.radians(a2)))]
    wedge = prism2d(wp, 10.40, 11.60)
    r = as_solid(outer.cut(keep).intersect(wedge))
    return r

for sgn, _t in ((+1, "r"), (-1, "l")):
    _cc = arc_chamfer_cutter(sgn)
    if _cc is not None:
        if sgn > 0:
            tray_r = cut(tray_r, _cc)
        else:
            tray_l = cut(tray_l, _cc)
tray_r = report("tray-right+chamfer", tray_r)
tray_l = report("tray-left+chamfer", tray_l)
infill = report("infill+chamfer", infill)

# ================================================================ EXPORTS
# PO 2026-11-21: the lid is INTEGRAL with the north band — one
# north shelf (11 -> 9 parts). CORRECTION round (PO 2026-11-22):
# the shelf is cover + both band plateaus again (the trim
# round's cover-only shelf overshot the PO's instruction); the
# bands end at X +-152.30 (outermost keycap extent 151.001 +
# the 1.30 cap-gap margin), clean vertical end faces — only the
# portions beyond the outermost keys are removed. The north
# face stays flush at Y -64.37 over the shelf's span (for
# |X| > ~118 the north edge follows the tray outline, as built),
# top at the keytop datum 22.00.
shelf = report("north-shelf", fuse(cover, strip_l, strip_r))

# ============================================================ HINGE + LATCH (A)
# PO 2026-11-22, battery-swap idea 2 of the Opus study: the shelf
# no longer comes off — it OPENS on a hinge and is held by ONE
# finger latch. Premise change recorded: this supersedes the
# removal half of the 2026-11-21 lid-integral decision (the lid
# stays integral with the band — one part — either way).
# Placement by measurement (probe_hinge*.py): the only straight
# southern boundary of the shelf is the lid's south edge, and the
# bay south wall is board-free only for |X| <= 10.90 (the Wing
# boards' south edges cross the wall band from |X| 11.14 out,
# measured intersections 9.47 / 7.20 mm3 against wall posts at
# X 14..18 / 25..28) — so the hinge groups sit centrally on the
# wall: per side boss X +-(0.5..4.0), shelf knuckle +-(4.3..8.6),
# boss +-(8.9..10.9). Axis A = (Y -0.57, Z 19.30) on the lid's
# south edge line; wrap radius 2.70 (cylinder top exactly 22.00 —
# nothing above Z22, nothing past the north face). TWO pins,
# one per side: O2.0 non-magnetic (SUS316/brass — ferromagnetic
# parts near the Wing Hall sensors are prohibited), shaft from
# the boss1 inner face (|X| 0.5) to tip |X| 10.80 in the boss2
# blind hole (floor 10.85), head flange O3.4 x 0.4 at the centre
# (X 0.1..0.5 / -0.5..-0.1 — the 1.0 centre gap takes both
# flanges side by side); each pin is inserted from the bay
# centre outward after the plates are on and is captive between
# its head and the blind floor. (A single centre-spanning pin
# measured 0.628 mm3 into the lid's south edge at the centre
# gap — the axis lies on the edge line — hence two pins.)
# Holes O2.1; the knuckle holes are slotted +0.3 in Y so closed
# positioning is by the north sandwich + underside, not the pin.
# Knuckle wall (5.4-2.1)/2 = 1.65. Boss posts stand on the wall
# (top 15.15), embedded from Z 4.0; the shelf is notched at the
# boss spans (boss1 notch from X 0.0 so the pin heads sit in it).
AX_Y, AX_Z, AX_R = -0.57, 19.30, 2.70


def xcyl(x0, x1, r, cy=AX_Y, cz=AX_Z):
    """Cylinder along +X from x0 to x1, axis at (cy, cz)."""
    return bd.Solid.make_cylinder(
        r, x1 - x0, bd.Plane(origin=(x0, cy, cz),
                             x_dir=(0, 1, 0), z_dir=(1, 0, 0)))


def boss(part, xa, xb, hole_xa, hole_xb):
    """One hinge boss: post on the bay wall + pin wrap + hole."""
    part = fuse(part, box(xa, xb, -2.37, -0.37, 4.0, AX_Z),
                xcyl(xa, xb, AX_R))
    return cut(part, xcyl(hole_xa, hole_xb, 1.05))


# boss1 both sides + boss2 right on the infill (its wall span);
# boss2 left on tray-left (the infill ends at X -6). The boss2
# holes are blind, floor at |X| 10.85 (pin tips at 10.80).
infill = boss(infill, 0.5, 4.0, 0.2, 4.3)
infill = boss(infill, -4.0, -0.5, -4.3, -0.2)
infill = boss(infill, 8.9, 10.9, 8.6, 10.85)
tray_l = boss(tray_l, -10.9, -8.9, -10.85, -8.6)
infill = report("infill+hinge", infill)
tray_l = report("tray-left+hinge", tray_l)

# Opening stop: a post on the shell-central at X -0.45..+0.45 —
# the gap between the two boss1 wraps (a wider post at
# X -2.6..-0.8 measured 0.255 mm3 into the west wrap). It stands
# on the shell (top 10.90; the Main board is below the shell
# here, so its centre tongue is irrelevant). The standing
# shelf's lid top edge lands on its top (Z 19.10); the contact
# angle is sweep-verified (target ~95 deg).
shell = fuse(shell, box(-0.45, 0.45, 1.88, 3.38, 10.0, 19.10))
shell = report("shell-central+stop", shell)

# Shelf knuckles + pin slots + boss notches.
for sgn in (+1, -1):
    def X(a, b, s=sgn):
        return (a, b) if s > 0 else (-b, -a)
    xa, xb = X(4.3, 8.6)
    shelf = fuse(shelf, xcyl(xa, xb, AX_R))
    shelf = cut(shelf, xcyl(xa, xb, 1.05, cy=AX_Y - 0.15),
                xcyl(xa, xb, 1.05, cy=AX_Y + 0.15),
                box(xa, xb, AX_Y - 0.15, AX_Y + 0.15,
                    AX_Z - 1.05, AX_Z + 1.05))
    for (a, b) in ((0.0, 4.3), (8.6, 11.2)):
        xa, xb = X(a, b)
        shelf = cut(shelf, box(xa, xb, -3.5, 2.4, 15.0, 22.3),
                    box(xa, xb, -2.67, -0.17, 10.9, 15.6))
# E/W skirt fin north-end trim (arc-sweep finding): the fins
# (X +-(28.25..30.25), Z 11.15..15.35) hang with their north
# faces coplanar with the bay north wall's inner face
# (Y -62.37); rotating about the south axis, their bottom
# corners (rel dy -61.80, dz -8.15, radius 62.33 > 61.80) swing
# north and clip the wall's top inner corner (measured
# 0.700 mm3/side at 2.5 deg). Shortening the fins' low north
# ends to Y -61.57 (rel dy -61.00, max radius 61.54 < 61.80)
# clears the swing; the lid above is untouched.
for sgn in (+1, -1):
    xa, xb = (28.25, 30.25) if sgn > 0 else (-30.25, -28.25)
    shelf = cut(shelf, box(xa, xb, -62.37, -61.57, 11.0, 15.35))
shelf = report("north-shelf+hinge", shelf)

# ============================================================ LATCH, RELOCATED (trim round)
# TRIM round (PO 2026-11-22): the latch's original seat — slider
# at X +85 on the right plateau, receiver in tray-right — sat ON
# the right arm the PO cut removes, so the seat is relocated
# into the remaining shelf span. The MECHANISM is unchanged
# (slider in a top groove + stem through a web slot + collar in
# a pocket under a fixed web, keyhole entries at the two slide
# positions, PETG centring finger; 1 mm lift test is the proof;
# release = slide +-3.8). The old receiver cuts in tray-right
# are REMOVED (the +85 tray area returns to plain fill).
# New seat (probe_trim*.py): the bay north wall rib inside the
# lid span (top 15.15, Y -64.37..-62.0, lid underside 15.35).
# The rib is only ~2.4 wide in Y and the middle-cell face
# (Y -59.37) is 4.99 from the north face, so the round O4.4
# collar cannot be pocketed there; the collar becomes a BAR
# (4.4 in X x 2.2 in Y x 0.75) and the stem narrows to 1.2 in Y.
# Stem centre (12, -62.55): bar spans Y -63.65..-61.45 (pocket
# north wall 0.57 of rib face material; cell-face clearance
# 1.92); the web (rib top 14.15..15.15) retains the bar over a
# 1.28 Y-chord; the keyhole entries open to the north face so
# the bar's arc drift (northward, 0.16 by web exit) cannot jam.
# X = +12, NOT the centre: the wall's middle span (|X| <= 7.5)
# is capped at 7.80 (the cover skirt's span) and has no web at
# pocket height — the first build sat the receiver at X 0 and
# the lift proof read 0.000 (nothing to engage); the rib top
# 15.15 is measured at |X| 12..20 (probe_trim). The receiver
# straddles centre-infill (X ..13) and tray-right (13..) — cut
# from both. The lid stem slot spans the bar's full travel
# sweep (centre +-6.2) so the bar clears the north skirt.
shelf = cut(shelf,
            box(-2.3, 26.3, -63.35, -56.75, 19.8, 22.5),
            box(11.0, 13.0, -61.25, -59.35, 19.05, 19.8),
            box(5.8, 18.2, -63.80, -61.80, 12.90, 22.5))
shelf = report("north-shelf+latch", shelf)
for _host in ("infill", "tray_r"):
    _p = infill if _host == "infill" else tray_r
    _p = cut(_p,
             box(5.6, 18.4, -63.80, -61.40, 13.30, 14.15),
             box(5.8, 18.2, -63.25, -61.85, 14.15, 15.20),
             box(13.4, 18.2, -64.37, -61.40, 14.15, 15.20),
             box(5.8, 10.6, -64.37, -61.40, 14.15, 15.20))
    if _host == "infill":
        infill = report("infill+latch", _p)
    else:
        tray_r = report("tray-right+latch", _p)

# Latch slider (printed part, built at the centred/locked
# position): body in the lid groove, grip grooves on top (top
# stays flush 22.00), stem down the web slot, bar collar in the
# rib pocket. The PETG finger under the body (arm 7 long x 0.6
# thick, tooth into the groove-floor dip) centres the slider on
# release — unloaded in the dip (locked), max strain ~1.3% at
# full travel (as the original site).
sl = box(2.0, 22.0, -62.85, -57.25, 19.8, 22.0)
for gx in (5.5, 10.5, 15.5):
    sl = cut(sl, box(gx, gx + 1.2, -62.85, -57.25, 21.5, 22.5))
sl = cut(sl, box(11.5, 21.0, -61.05, -59.55, 19.8, 20.7))
sl = fuse(sl,
          box(19.5, 22.0, -61.05, -59.55, 19.85, 20.55),
          box(12.3, 19.5, -61.05, -59.55, 19.90, 20.50),
          box(11.9, 12.9, -61.05, -59.55, 19.05, 20.00),
          box(11.0, 13.0, -63.15, -61.95, 14.10, 20.2),
          box(9.8, 14.2, -63.65, -61.45, 13.35, 14.10))
slider = report("latch-slider", sl)

# Trim the shell by the fixed trays/infill: the (B) flat sheet
# (Z 8.90..10.90 over the pre-revision footprint) overlaps
# tray-left's top by 3.993 mm3 at its north-west (measured);
# wherever a tray already provides the 10.90 surface the sheet
# is redundant. Coincident resting faces are unaffected.
shell = cut(shell, tray_l, tray_r, infill)
shell = report("shell-central+trim", shell)

# ================================================================ TRACKPAD COVER (PO 2026-11-22)
# PO: 「トラックパッド周りの上蓋も設計して」 — a bezel finishing
# the trackpad surround. Measured starting state (probe_padcover*):
# module Cirque TM040040 Ø40 body / Ø38 sensing, centre (0,48),
# top Z12.70, bottom 11.20; seat = Ø44.6 recess, floor 11.10 where
# the slab is thick, 10.90 patches elsewhere; the island leftovers
# preserved by the old keep-disc exemption (E/W rim bumps 12.55,
# north rise to ~15.1 at r<=23.5) poke into the cover's footprint;
# shell slab is uniformly 10.90..8.90 at all four screw points;
# shell south edge at Y 69.70 = 21.7 from the pad centre (the
# cover's cone foot cannot close toward S); SW1 plunger centre
# (-15.5, 64.50) is 22.64 from the pad centre, head Ø4 top 12.10.
#
# Shell changes:
# (1) Island trim: within r25.6 of (0,48) the shell is cut to
#     Z <= 11.25 — the exemption leftovers go, completing the
#     slope-removal flattening inside the cover footprint; the
#     seat rim becomes uniform (floor 11.10 / rim 11.25).
# (2) Four screw bosses under the field at r25.5, angles
#     30/150/210/330 deg from the pad centre: Ø6.0, Z 7.30..9.60
#     (fused into the 8.90 slab underside; bottom 7.30 = 1.40
#     above the Main top 5.90), with Ø1.6 pilot holes through
#     boss + slab. Boss x tray/infill measured 0.000 beforehand;
#     the seat opening (X +-3, Y 26..30) and the whole
#     below-shell connector zone are untouched.
import math as _math
PAD_C = (0.0, 48.0)
SCREW_PTS = []
for _a in (30, 150, 210, 330):
    _t = _math.radians(_a)
    SCREW_PTS.append((PAD_C[0] + 25.5 * _math.cos(_t),
                      PAD_C[1] + 25.5 * _math.sin(_t)))
shell = cut(shell, cyl(PAD_C[0], PAD_C[1], 25.6, 11.25, 30.0))
shell = report("shell-central+padtrim", shell)
for (sx, sy) in SCREW_PTS:
    shell = fuse(shell, cyl(sx, sy, 3.0, 7.30, 9.60))
for (sx, sy) in SCREW_PTS:
    shell = cut(shell, cyl(sx, sy, 0.8, 7.0, 11.2))
shell = report("shell-central+padboss", shell)

# Cover (built in local frame, axis = Z through the pad centre,
# then moved to (0,48)): revolved annulus profile (r, Z):
#   window wall r20.20 (0.20 clear of the Ø40 module; NO overlap
#   of the module at any height -> the cover cannot pinch it),
#   window top edge chamfer 0.32x0.32, top ring at Z12.70 = flush
#   with the pad surface, outer cone 34.7 deg down to a foot ring
#   resting on the 10.90 field (r24.40..25.60), underside 11.35
#   (0.25 over the seat floor, 0.10 over the trimmed rim), inner
#   skirt r20.20..21.00 down to 11.25 (0.15 over the floor)
#   dipping into the annular gap.
_prof = [(20.20, 11.25), (20.20, 12.38), (20.52, 12.70),
         (23.00, 12.70), (25.60, 10.90), (24.40, 10.90),
         (24.40, 11.35), (21.00, 11.35), (21.00, 11.25)]
_wire = bd.Wire.make_polygon(
    [bd.Vector(r, 0, z) for (r, z) in _prof] +
    [bd.Vector(_prof[0][0], 0, _prof[0][1])])
cover = bd.revolve(bd.Face(_wire), bd.Axis.Z, 360)
cover = cover.moved(bd.Location((PAD_C[0], PAD_C[1], 0)))
# Screw ears: flat pads (top 11.90) on the cone at the 4 screw
# angles, radial span r22.8..28.2, tangential width 9.0, foot on
# the field; Ø2.2 clearance hole + flat-head countersink
# (r1.1 -> r1.7 over Z 11.20..11.90) at r25.5.
for _a in (30, 150, 210, 330):
    _t = _math.radians(_a)
    _u = bd.Vector(_math.cos(_t), _math.sin(_t), 0)
    _v = bd.Vector(-_math.sin(_t), _math.cos(_t), 0)
    _org = (bd.Vector(PAD_C[0], PAD_C[1], 10.90)
            + _u * 22.8 + _v * (-4.5))
    _pl = bd.Plane(origin=_org, x_dir=_u, z_dir=(0, 0, 1))
    cover = fuse(cover, bd.Solid.make_box(5.4, 9.0, 1.0, _pl))
for (sx, sy) in SCREW_PTS:
    cover = cut(cover, cyl(sx, sy, 1.1, 10.80, 11.95),
                bd.Solid.make_cone(1.1, 1.7, 0.7,
                                   bd.Plane(origin=(sx, sy, 11.20))))
# South: the shell edge (Y 69.70) truncates the cone; the cover
# is clipped at Y 69.00 (0.70 inside the edge) and the top corner
# gets a dimensioned 45 deg chamfer (67.90,12.70)->(69.00,11.60);
# below it the clipped face drops to the underside (0.35 shadow
# gap over the field — an intended joint, no upward catch).
cover = cut(cover, box(-40, 40, 69.0, 95.0, 0.0, 30.0))
_wedge = bd.Face(bd.Wire.make_polygon(
    [bd.Vector(0, 67.90, 12.70), bd.Vector(0, 72.00, 8.60),
     bd.Vector(0, 72.00, 20.00), bd.Vector(0, 67.90, 20.00),
     bd.Vector(0, 67.90, 12.70)]))
_w = bd.extrude(_wedge, 34.0)
_wbb = _w.bounding_box()
_w = _w.moved(bd.Location((-(_wbb.min.X + _wbb.max.X) / 2.0, 0, 0)))
cover = cut(cover, _w)
# SW1 plunger notch: Ø5.2 clearance cylinder at the plunger
# centre through the whole cover (head r2.0 -> 0.60 plan
# clearance at every height, rest or pressed; the notch opens
# through the cone, so the head stays side-accessible and
# pressable exactly as on the open field).
cover = cut(cover, cyl(-15.5, 64.50, 2.6, 5.0, 23.0))
# Conform the underside to the finished shell (the project's
# own idiom, cf. the shell's tray trim): the north ears' flat
# 10.90 bottoms otherwise cut 2 x 1.750 mm3 into the trimmed
# island shoulder, which still rises to 11.25 inside r25.6.
# Face contacts (foot ring, ear seats at the screw points,
# where the field is a flat 10.90) are zero-volume and stay.
cover = cut(cover, shell)
cover = report("trackpad-cover", cover)

parts = {
    "tray-left": tray_l, "tray-right": tray_r, "centre-infill": infill,
    "shell-central": shell, "north-shelf": shelf,
    "plate-left": plate_l, "plate-right": plate_r,
    "plunger-sw1": plunger, "light-pipe-dled": pipe,
    "latch-slider": slider, "trackpad-cover": cover,
}
for name, s in parts.items():
    bd.export_step(s, f"{OUT}/{name}.step")
    bd.export_stl(s, f"{OUT}/{name}.stl")
    bd.export_brep(s, f"{ASM}/{name}.brep")
print("exported", len(parts), "parts to", OUT)
json.dump({"fly_centre": [38, -60.00]}, open(f"{ASM}/params.json", "w"))
