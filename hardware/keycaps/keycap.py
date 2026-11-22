"""Parametric keycap for he-piantor-42 (Issue #296 keycap design).

Design record: .issue296-keycaps-runtime/keycap-plan.md and
hardware/keycaps/DESIGN.md. Interface: Gateron Magnetic Jade Pro HE
(KS-20TF10B045NW-Y106), drawing SPEC-KS-20T-041 — MX cross stem
4.00 +/- 0.05 overall, arms 1.30 +/- 0.04 (N-S arm, thickness in X)
and 1.10 +/- 0.04 (E-W arm, thickness in Y); travel 3.5 +/- 0.2.

Local frame: origin at the key centre, z = 0 at the switch-plate top
surface (case Z 10.90), +z up. The cap is built in its rest
(unpressed) position.

Pitch-dependent dimensions: cap outer width W = pitch - GAP_NOMINAL
and, through it, the skirt wall thickness (the cavity width is fixed
by the switch housing). Everything else is pitch-independent.
"""
import math
import os

import build123d as bd

# ---- fixed interface values (from the record, see DESIGN.md) ----
TRAVEL_MAX = 3.7            # drawing travel 3.5 +/- 0.2, worst descent
HOUSING_BODY_MAX = 14.05    # housing body 14.00 +/- 0.05
LEDGE_Z = 6.10              # cover ledge above plate (11.10 - 5.00)
STEM_TIP_Z = 10.10          # drawing-measured (finding F1), plate frame
CAVITY_W = 14.45            # housing max + 0.20/side (play + print tol)
CAVITY_R = 1.0              # corner radius: the diagonal clearance is
                            # set by both corners' radii (DESIGN.md);
                            # R1.0 keeps >= +0.08 even against an R0.5
                            # housing corner
CAVITY_CEIL_Z = 10.00       # >= ledge + travel max + 0.20
SOCKET_CEIL_Z = 10.15       # stem tip + 0.05
BOSS_W = 5.60               # socket boss outer (square)
BOSS_BOTTOM_Z = 8.10        # engagement = STEM_TIP_Z - BOSS_BOTTOM_Z = 2.00
CROSS_SPAN = 4.24           # socket cross overall opening (tip clearance)
ARM_NS = 1.30               # stem arm running N-S: thickness in X
ARM_EW = 1.10               # stem arm running E-W: thickness in Y
SLOT_BIAS = -0.02           # nominal interference bias on arm slots
TOP_Z = 11.10               # cap top: case Z 22.00 datum preserved
SKIRT_BOTTOM_Z = 4.40       # >= travel max + flange top 0.50 + 0.20
CORNER_R = 2.0
# Dish (round 2, Junana-feel): cylindrical pocket, axis // Y, inside
# a rim land RIM_W wide per side that stays at TOP_Z. The pocket
# half-chord is a = W/2 - RIM_W; R follows from a and the depth.
# Depth is capped by the wall over the socket ceiling:
# (TOP_Z - s) - SOCKET_CEIL_Z >= MIN_TOP_WALL  ->  s <= 0.60.
RIM_W = 1.50                # rim land per side (left/right)
DISH_DEPTH = 0.50           # primary variant
DISH_VARIANTS = (0.35, 0.50, 0.60)  # shallow / primary / deep(cap)
MIN_TOP_WALL = 0.35         # min material over the socket ceiling
TOP_CHAMFER = 0.30
GAP_NOMINAL = 0.50          # D-002 rationale: 16.5 cap at 17 pitch


def _rr_face(w, r):
    """Rounded-rectangle face centred on origin (XY plane)."""
    with bd.BuildSketch() as sk:
        with bd.BuildLine():
            l1 = bd.Line((-w / 2 + r, -w / 2), (w / 2 - r, -w / 2))
            a1 = bd.RadiusArc((w / 2 - r, -w / 2), (w / 2, -w / 2 + r), r)
            l2 = bd.Line((w / 2, -w / 2 + r), (w / 2, w / 2 - r))
            a2 = bd.RadiusArc((w / 2, w / 2 - r), (w / 2 - r, w / 2), r)
            l3 = bd.Line((w / 2 - r, w / 2), (-w / 2 + r, w / 2))
            a3 = bd.RadiusArc((-w / 2 + r, w / 2), (-w / 2, w / 2 - r), r)
            l4 = bd.Line((-w / 2, w / 2 - r), (-w / 2, -w / 2 + r))
            a4 = bd.RadiusArc((-w / 2, -w / 2 + r), (-w / 2 + r, -w / 2), r)
        bd.make_face()
    return sk.face()


def _prism(w, r, z0, z1):
    f = _rr_face(w, r)
    return bd.Solid.extrude(f, bd.Vector(0, 0, z1 - z0)).moved(
        bd.Location(bd.Vector(0, 0, z0)))


def _box(w, z0, z1):
    return bd.Solid.make_box(w, w, z1 - z0,
                             bd.Plane(origin=(-w / 2, -w / 2, z0)))


def _cross_prism(span, slot_x, slot_y, z0, z1):
    """Cross-shaped prism: slot_x = X-width of the Y-long slot (for the
    N-S arm), slot_y = Y-width of the X-long slot (for the E-W arm)."""
    a = bd.Solid.make_box(slot_x, span, z1 - z0,
                          bd.Plane(origin=(-slot_x / 2, -span / 2, z0)))
    b = bd.Solid.make_box(span, slot_y, z1 - z0,
                          bd.Plane(origin=(-span / 2, -slot_y / 2, z0)))
    return a.fuse(b)


def dish_radius(pitch, dish_depth):
    """Cylinder R for the pocket: half-chord a = W/2 - RIM_W, depth s."""
    a = (pitch - GAP_NOMINAL) / 2 - RIM_W
    return (a * a + dish_depth * dish_depth) / (2 * dish_depth)


def build_cap(pitch=17.0, socket_offset=0.0, dish_depth=DISH_DEPTH):
    """Return the keycap solid for the given pitch (mm).

    socket_offset is added to both arm-slot widths; it is the
    printer-calibration parameter set by the fit coupon (see
    DESIGN.md). The cross span (arm-tip clearance) is not offset.
    dish_depth selects the top-pocket variant (DISH_VARIANTS).
    """
    assert dish_depth <= TOP_Z - SOCKET_CEIL_Z - MIN_TOP_WALL + 1e-9, (
        f"dish_depth {dish_depth} leaves < {MIN_TOP_WALL} mm over the "
        f"socket ceiling")
    W = pitch - GAP_NOMINAL
    height = TOP_Z - SKIRT_BOTTOM_Z

    # outer shell
    cap = _prism(W, CORNER_R, SKIRT_BOTTOM_Z, TOP_Z)

    # top dish: cylindrical pocket, axis // Y, floor at TOP_Z - s at
    # centre, rising to TOP_Z at |x| = a = W/2 - RIM_W. The cutter is
    # the cylinder clipped to |x| <= a, so the rim land at TOP_Z is
    # never cut. The trough stays open front/back (cylinder // Y).
    a = W / 2 - RIM_W
    s = dish_depth
    R = (a * a + s * s) / (2 * s)
    zc = (TOP_Z - s) + R  # cylinder centre height
    cyl = bd.Solid.make_cylinder(R, W + 10,
                                 bd.Plane(origin=(0, -(W + 10) / 2, zc),
                                          x_dir=(1, 0, 0), z_dir=(0, 1, 0)))
    clip = bd.Solid.make_box(2 * a, W + 10, s + 2.0,
                             bd.Plane(origin=(-a, -(W + 10) / 2,
                                              TOP_Z - s - 1.0)))
    dish_parts = cyl.intersect(clip)
    dish = dish_parts[0]
    for extra in dish_parts[1:]:
        dish = dish.fuse(extra)
    cap = cap.cut(dish)

    # top perimeter chamfer (best effort; geometry is valid without
    # it). Restricted to edges near the plan outline so the new
    # pocket-boundary edges at TOP_Z are NOT chamfered.
    try:
        top_edges = [e for e in cap.edges()
                     if abs(e.center().Z - TOP_Z) < 0.35 and e.length > 1.0
                     and (abs(e.center().X) > W / 2 - 0.6
                          or abs(e.center().Y) > W / 2 - 0.6)]
        if top_edges:
            cap = bd.chamfer(top_edges, TOP_CHAMFER)
    except Exception:
        pass

    # inner cavity (open at the bottom)
    cap = cap.cut(_prism(CAVITY_W, CAVITY_R, SKIRT_BOTTOM_Z - 1.0,
                         CAVITY_CEIL_Z))

    # socket boss (hangs below the cavity ceiling, inside the top wall)
    cap = cap.fuse(_box(BOSS_W, BOSS_BOTTOM_Z, SOCKET_CEIL_Z + 0.05))

    # cross socket: flared mouth (first 0.30 of depth, +0.30) then the
    # calibrated slots up to the socket ceiling.
    slot_x = ARM_NS + SLOT_BIAS + socket_offset
    slot_y = ARM_EW + SLOT_BIAS + socket_offset
    cap = cap.cut(_cross_prism(CROSS_SPAN + 0.30, slot_x + 0.30,
                               slot_y + 0.30, BOSS_BOTTOM_Z - 0.05,
                               BOSS_BOTTOM_Z + 0.30))
    cap = cap.cut(_cross_prism(CROSS_SPAN, slot_x, slot_y,
                               BOSS_BOTTOM_Z + 0.30, SOCKET_CEIL_Z))
    return cap.clean() if hasattr(cap, "clean") else cap


def build_coupon(offsets=(-0.05, 0.0, 0.05, 0.10, 0.15)):
    """Fit-calibration coupon: socket test blocks on a base web.

    Each block is BOSS_W square in section with the same socket as the
    cap (same boss bottom / ceiling relationship, truncated), one per
    socket_offset, laid left -> right in ascending offset order.
    Print in the production PETG + settings, press onto a real Jade
    Pro stem, pick the offset that seats fully by hand and pulls off
    with a keycap puller without cracking.
    """
    blocks = []
    pitch_x = 9.0
    x0 = -pitch_x * (len(offsets) - 1) / 2
    depth = SOCKET_CEIL_Z - BOSS_BOTTOM_Z
    for i, off in enumerate(offsets):
        cx = x0 + i * pitch_x
        blk = bd.Solid.make_box(BOSS_W + 2.4, BOSS_W + 2.4, depth + 1.6,
                                bd.Plane(origin=(cx - (BOSS_W + 2.4) / 2,
                                                 -(BOSS_W + 2.4) / 2, 0)))
        slot_x = ARM_NS + SLOT_BIAS + off
        slot_y = ARM_EW + SLOT_BIAS + off
        cut = _cross_prism(CROSS_SPAN + 0.30, slot_x + 0.30, slot_y + 0.30,
                           1.6 - 0.05, 1.6 + 0.30).moved(
                               bd.Location(bd.Vector(cx, 0, 0)))
        cut2 = _cross_prism(CROSS_SPAN, slot_x, slot_y, 1.6 + 0.30,
                            1.6 + depth).moved(bd.Location(bd.Vector(cx, 0, 0)))
        blk = blk.cut(cut).cut(cut2)
        # index notch on the front edge: i+1 grooves
        for k in range(i + 1):
            gx = cx - 2.0 + k * 1.0
            blk = blk.cut(bd.Solid.make_box(
                0.5, 0.6, depth + 1.6,
                bd.Plane(origin=(gx, -(BOSS_W + 2.4) / 2 - 0.01, 0))))
        blocks.append(blk)
    web = bd.Solid.make_box(pitch_x * (len(offsets) - 1) + BOSS_W + 4.4,
                            BOSS_W + 2.4, 1.2,
                            bd.Plane(origin=(-(pitch_x * (len(offsets) - 1)
                                               + BOSS_W + 4.4) / 2,
                                             -(BOSS_W + 2.4) / 2, -1.2)))
    out = web
    for b in blocks:
        out = out.fuse(b)
    return out


def export_all(outdir):
    os.makedirs(outdir, exist_ok=True)
    for pitch in (17.0, 16.0):
        tag = f"p{int(pitch)}"
        for s in DISH_VARIANTS:
            cap = build_cap(pitch, dish_depth=s)
            suffix = "" if s == DISH_DEPTH else f"-dish{int(round(s * 100)):03d}"
            bd.export_step(cap, os.path.join(
                outdir, f"keycap-{tag}{suffix}.step"))
            bd.export_stl(cap, os.path.join(
                outdir, f"keycap-{tag}{suffix}.stl"))
            print(f"{tag}{suffix or ' (primary)'}: W="
                  f"{pitch - GAP_NOMINAL:.2f} dish={s:.2f} "
                  f"R={dish_radius(pitch, s):.1f} vol={cap.volume:.1f} mm^3 "
                  f"bbox={cap.bounding_box().min} .. "
                  f"{cap.bounding_box().max}")
    cpn = build_coupon()
    bd.export_step(cpn, os.path.join(outdir, "socket-coupon.step"))
    bd.export_stl(cpn, os.path.join(outdir, "socket-coupon.stl"))
    print(f"coupon vol={cpn.volume:.1f} mm^3")


if __name__ == "__main__":
    export_all(os.path.dirname(os.path.abspath(__file__)))
