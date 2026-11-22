"""Fit verification for the Issue #296 keycap design.

Numbers, not impressions. Checks (see DESIGN.md / keycap-plan.md):
 1. Model sanity + measured wall thickness from a mid-height section.
 2. Socket vs stem cross (drawing tolerances), across coupon offsets.
 3. Plan view at the real layout (caps.json poses, 17 mm class):
    cap-to-cap min distance, outermost |X|, shelf stack-up re-run
    with the designed cap replacing the ASSUMED Junana values.
 4. 16 mm variant: local 3x3 grid gap + skirt wall vs FDM floor.
 5. Bottom-out (descent = travel max 3.7): cap solid vs plate and
    vs the fixed housing envelope, with and without the assumed
    stem bore (the bore is a named assumption, print-gate item).

Run: ~/workspace/tools/cad-venv/bin/python verify_keycaps.py
"""
import json
import math
import os
import sys

import build123d as bd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import keycap as kc

RT = os.path.expanduser("~/workspace/projects/he-piantor-keycaps/"
                        ".issue296-runtime")
PRINT_TOL = 0.20        # FDM PETG XY, the case's own assumption
PLAY = 0.15             # cap seating play (case P0/P1, issue-150)
CENTRE_OFF = 0.10       # centre offset per side (issue-150 budget)
WALL_FLOOR = 0.80       # FDM reliable wall floor


def rr_outline(w, r, n_arc=12):
    """Rounded-rect outline points (CCW), centred on origin."""
    pts = []
    corners = [(w / 2 - r, w / 2 - r, 0), (w / 2 - r, -w / 2 + r, -90),
               (-w / 2 + r, -w / 2 + r, 180), (-w / 2 + r, w / 2 - r, 90)]
    # walk the boundary: arcs centred at the four corner centres
    centres = [(w / 2 - r, w / 2 - r), (-w / 2 + r, w / 2 - r),
               (-w / 2 + r, -w / 2 + r), (w / 2 - r, -w / 2 + r)]
    starts = [0, 90, 180, 270]
    for (cx, cy), a0 in zip(centres, starts):
        for i in range(n_arc + 1):
            a = math.radians(a0 + 90 * i / n_arc)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return np.array(pts)


def _pt_edge_dists(P, A):
    """Distance from each point in P (n,2) to each edge of polygon A
    (m,2, closed). Returns (n,m)."""
    E0 = A
    E1 = np.roll(A, -1, axis=0)
    AB = E1 - E0
    denom = np.einsum('ij,ij->i', AB, AB)
    AP = P[:, None, :] - E0[None, :, :]
    t = np.einsum('ijk,jk->ij', AP, AB) / np.maximum(denom, 1e-12)
    t = np.clip(t, 0.0, 1.0)
    proj = E0[None, :, :] + t[:, :, None] * AB[None, :, :]
    return np.linalg.norm(P[:, None, :] - proj, axis=2)


def _inside_convex(p, A):
    """True if point p is inside convex polygon A (either winding)."""
    E0 = A
    E1 = np.roll(A, -1, axis=0)
    cr = ((E1[:, 0] - E0[:, 0]) * (p[1] - E0[:, 1])
          - (E1[:, 1] - E0[:, 1]) * (p[0] - E0[:, 0]))
    return cr.min() >= -1e-9 or cr.max() <= 1e-9


def poly_dist(A, B):
    """Min distance between two CONVEX polygons (point lists, closed
    implicitly). Exact for convex shapes: min vertex-to-edge distance,
    or 0 if one contains a vertex of the other."""
    if _inside_convex(A[0], B) or _inside_convex(B[0], A):
        return 0.0
    return min(_pt_edge_dists(A, B).min(), _pt_edge_dists(B, A).min())


def rot(pts, deg):
    a = math.radians(deg)
    R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    return pts @ R.T


print("=" * 72)
print("1. MODEL SANITY + WALL (from solids)")
for pitch in (17.0, 16.0):
    cap = kc.build_cap(pitch)
    solids = cap.solids()
    bb = cap.bounding_box()
    W = pitch - kc.GAP_NOMINAL
    # section at z=6.0: intersect with a thin slab, read wire bboxes
    slab = bd.Solid.make_box(60, 60, 0.02, bd.Plane(origin=(-30, -30, 6.0)))
    sec = cap.intersect(slab)
    wires_bb = []
    for f in sec.faces():
        for w_ in f.wires():
            wires_bb.append(w_.bounding_box())
    widths = sorted(round(b.max.X - b.min.X, 3) for b in wires_bb)
    wall = (W - kc.CAVITY_W) / 2
    print(f" pitch {pitch:.0f}: solids={len(solids)} vol={cap.volume:.1f} "
          f"bbox X {bb.min.X:.3f}..{bb.max.X:.3f} Z {bb.min.Z:.3f}.."
          f"{bb.max.Z:.3f}")
    print(f"   section@z6 wire widths={widths} (outer W={W:.2f}, cavity "
          f"{kc.CAVITY_W}) -> skirt wall analytic {wall:.3f} "
          f"{'OK' if wall >= WALL_FLOOR else 'BELOW FDM FLOOR ' + str(WALL_FLOOR)}")

print("=" * 72)
print("2. SOCKET vs STEM CROSS (drawing: cross 4.00+/-0.05, arms "
      "1.30+/-0.04 / 1.10+/-0.04)")
print(f" cross span {kc.CROSS_SPAN}: arm-tip clearance/side vs stem max "
      f"4.05 = {(kc.CROSS_SPAN - 4.05) / 2:.3f}; vs stem min 3.95 = "
      f"{(kc.CROSS_SPAN - 3.95) / 2:.3f}")
for off in (-0.05, 0.0, 0.05, 0.10, 0.15):
    sx = kc.ARM_NS + kc.SLOT_BIAS + off
    sy = kc.ARM_EW + kc.SLOT_BIAS + off
    print(f" offset {off:+.2f}: slotX {sx:.2f} vs arm 1.26..1.34 -> "
          f"fit {-1 * (sx - 1.34):+.2f}..{-1 * (sx - 1.26):+.2f} "
          f"(+ = interference) | slotY {sy:.2f} vs arm 1.06..1.14 -> "
          f"fit {-1 * (sy - 1.14):+.2f}..{-1 * (sy - 1.06):+.2f}")
print(" (nominal-only design cannot guarantee the fit: stem tol "
      "+/-0.04 against FDM +/-0.20 -> coupon calibration, DESIGN.md)")

print("=" * 72)
print("3. PLAN VIEW, REAL POSES (caps.json, 17 mm class)")
caps = json.load(open(os.path.join(RT, "caps.json")))
W17 = 17.0 - kc.GAP_NOMINAL
outline = rr_outline(W17, kc.CORNER_R)
# establish the rotation convention against caps.json's own polygons
k0 = caps["left"]["keys"][0]
p0 = np.array(caps["left"]["cap_polys"][0])
SGN = None
for sgn in (1, -1):
    sq = np.array([[W17 / 2, W17 / 2], [W17 / 2, -W17 / 2],
                   [-W17 / 2, -W17 / 2], [-W17 / 2, W17 / 2]])
    test = rot(sq, sgn * k0[2]) + np.array(k0[:2])
    # full point-set match (an X-only comparison cannot distinguish
    # the mirror: a square's sorted X multiset is identical for +/-)
    err = max(min(np.linalg.norm(test - p, axis=1)) for p in p0)
    if err < 1e-6:
        SGN = sgn
        break
assert SGN is not None, "rotation convention not found"
print(f" rotation convention: outline rotated by {SGN:+d} x keys angle "
      f"(asserted against caps.json polygons)")
placed = []
for side in ("left", "right"):
    for (x, y, ang) in caps[side]["keys"]:
        placed.append(rot(outline, SGN * ang) + np.array([x, y]))
mind, argmin = 1e9, None
for i in range(len(placed)):
    for j in range(i + 1, len(placed)):
        d = poly_dist(placed[i], placed[j])
        if d < mind:
            mind, argmin = d, (i, j)
print(f" cap-to-cap min distance (designed outline, nominal): {mind:.3f} "
      f"(pair {argmin}); nominal gap target {kc.GAP_NOMINAL:.2f}")
outer_x = max(np.abs(p[:, 0]).max() for p in placed)
print(f" outermost |X| of designed caps: {outer_x:.3f} "
      f"(case record with square caps: 151.001; shelf end at 152.30)")
# shelf stack-up re-run: northern growth with the designed cap.
# growth = extra northward reach of a max-size print (W + PRINT_TOL)
# over the nominal outline, worst key, minus the same for the case's
# assumed cap (W + 0.25 size tol, sharp square) computed identically.
def north_growth(w_new, w_nom, r_new, square=False):
    g = 0.0
    for side in ("left", "right"):
        for (x, y, ang) in caps[side]["keys"]:
            o_new = rot(rr_outline(w_new, r_new), SGN * ang)
            o_nom = rot(rr_outline(w_nom, kc.CORNER_R), SGN * ang)
            g = max(g, o_nom[:, 1].min() - o_new[:, 1].min())
    return g
g_design = north_growth(W17 + PRINT_TOL, W17, kc.CORNER_R)
g_assumed = north_growth(W17 + 0.25, W17, kc.CORNER_R)
print(f" northern growth term: designed (tol +/-0.20) {g_design:.3f} | "
      f"case's assumed (tol +/-0.25) {g_assumed:.3f}")
for name, g in (("designed", g_design), ("assumed", g_assumed)):
    rem = 1.30 - (g + PLAY + 0.20 + 0.30 + 0.10)
    print(f" shelf stack remainder [{name}]: 1.30 - (growth {g:.3f} + "
          f"play 0.15 + shelf tol 0.20 + placement 0.30 + plate 0.10) "
          f"= {rem:+.3f}  (case record with assumed cap: +0.35)")
stack_wc = kc.GAP_NOMINAL - PRINT_TOL - 2 * PLAY - 2 * CENTRE_OFF
stack_rss = kc.GAP_NOMINAL - math.sqrt(PRINT_TOL**2 + (2 * PLAY)**2
                                       + (2 * CENTRE_OFF)**2)
print(f" cap-to-cap tolerance stack: nominal {kc.GAP_NOMINAL:.2f}, "
      f"worst-case {stack_wc:+.2f} (touch at the extreme corner), "
      f"RSS-typical {stack_rss:+.2f}")

print("=" * 72)
print("4. 16 mm VARIANT, LOCAL GRID")
o16 = rr_outline(16.0 - kc.GAP_NOMINAL, kc.CORNER_R)
grid = [o16 + np.array([16.0 * i, 16.0 * j])
        for i in range(3) for j in range(3)]
gaps = [poly_dist(grid[i], grid[j]) for i in range(9) for j in range(i + 1, 9)
        if abs(i // 3 - j // 3) + abs(i % 3 - j % 3) == 1]
print(f" adjacent-pair gap at 16 mm pitch: {min(gaps):.3f} nominal; "
      f"skirt wall {(16.0 - kc.GAP_NOMINAL - kc.CAVITY_W) / 2:.3f} "
      f"< FDM floor {WALL_FLOOR} -> prototype-only (DESIGN.md)")

print("=" * 72)
print("5. BOTTOM-OUT (solid intersections, descent = 3.7 worst)")
cap = kc.build_cap(17.0)
cap_p = cap.moved(bd.Location(bd.Vector(0, 0, -kc.TRAVEL_MAX)))
# fixed housing envelope: body to the ledge + lower flange at plate
# level. The stem bore (assumed) is a 5.90 sq hole from the ledge
# down 2.0; the moving stem collar is not part of the fixed envelope.
body = kc._prism(kc.HOUSING_BODY_MAX, 1.0, 0.0, kc.LEDGE_Z)
# diagonal (45 deg) corner clearance, analytic: cavity corner reach
# minus housing corner reach along the diagonal
def _reach(half, r):
    return (half - r) * math.sqrt(2) + r
clr_diag = _reach(kc.CAVITY_W / 2, kc.CAVITY_R) - _reach(
    kc.HOUSING_BODY_MAX / 2, 1.0)
clr_diag_r05 = _reach(kc.CAVITY_W / 2, kc.CAVITY_R) - _reach(
    kc.HOUSING_BODY_MAX / 2, 0.5)
print(f" cavity corner diagonal clearance: {clr_diag:+.3f} vs R1.0 "
      f"housing corner, {clr_diag_r05:+.3f} vs R0.5 (side clearance "
      f"{(kc.CAVITY_W - kc.HOUSING_BODY_MAX) / 2:.2f})")
flange = bd.Solid.make_box(15.50, 15.20, 0.80,
                           bd.Plane(origin=(-7.75, -7.60, -0.30)))
bore = bd.Solid.make_box(5.90, 5.90, 2.0,
                         bd.Plane(origin=(-2.95, -2.95, kc.LEDGE_Z - 2.0)))
env_bore = body.fuse(flange).cut(bore)
env_solid = body.fuse(flange)
def vol_of(shape):
    if shape is None:
        return 0.0
    if hasattr(shape, "solids"):
        return sum(s.volume for s in shape.solids())
    return shape.volume


for name, env in (("with assumed bore", env_bore),
                  ("NO bore (solid ledge)", env_solid)):
    v_rest = vol_of(cap.intersect(env))
    v_press = vol_of(cap_p.intersect(env))
    print(f" envelope {name}: intersection at rest {v_rest:.3f} mm^3, "
          f"at full press {v_press:.3f} mm^3")
plate = bd.Solid.make_box(80, 80, 1.0, bd.Plane(origin=(-40, -40, -1.0)))
print(f" cap vs plate at full press: {vol_of(cap_p.intersect(plate)):.3f} "
      f"mm^3; skirt bottom at press z = {kc.SKIRT_BOTTOM_Z - kc.TRAVEL_MAX:.2f}")
print(f" boss bottom at press z = {kc.BOSS_BOTTOM_Z - kc.TRAVEL_MAX:.2f} "
      f"-> bore entry below ledge {kc.LEDGE_Z - (kc.BOSS_BOTTOM_Z - kc.TRAVEL_MAX):.2f} mm")
print(f" cap top (case Z): rest {10.90 + kc.TOP_Z:.2f}, pressed "
      f"{10.90 + kc.TOP_Z - kc.TRAVEL_MAX:.2f} (datum 22.00 preserved)")
print("=" * 72)
print("DONE")
