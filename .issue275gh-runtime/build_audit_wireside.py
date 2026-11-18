"""Issue #275 Phase 2 GH check — full build + audit at plate 12.95 (B=6.75).

Configuration: flipped Main (components down), GH side-entry at both ends,
14 OD-1.0 wires/side, order-preserving fan (pin 1 at the WEST end of
every row). Fixed bodies: #248 frontier library at s=-0.60 (= plate 12.95)
with documented exclusions/replacements:
  EXCLUDE tray-left/right (frontier tray is the pre-lever solid; replaced
    by the production floor slab below), splice-*, Main-GH-*-DRAWING-BOUND
    (normal-pose Rev.7 legacy), Main-study-* (replaced by X-mirrored,
    Z-flipped copies = flipped-pose component reservations),
    EZmate-Main-plug (normal-pose J4 plug; flipped J4 out of scope),
    shell-*/strip-*/shell-central/USB-reference-shell (#248 raised-shell
    configuration, not the adopted flat case; all Z >= 8.8, unreachable).
  ADD production floor slab (top 1.60; D-046 pocket X -6..13 / Y 28..48
    at 0.60), flipped Main-study mirrors, Main GH plug envelopes at the
    Rev.10 symmetric sites (underside). Wing GH plug envelopes are the
    library's underside-*-J_WING bodies (reserved 4.85 mm, Z 1.90..6.75).
Audit: bbox prefilter -> boolean Common volume; pairs with Common == 0
but bbox gap < 0.5 mm get an independent BRepExtrema distance (the #248
round-10 repair). Self-test: a deliberately floor-shifted wire copy MUST
report contact, and the Wing plug envelope at s=-2.65 (plate 10.90) MUST
intersect the floor slab (Q1 quantification).
"""
import json, math, sys
import numpy as np
_P248 = '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
sys.path.insert(0, _P248 + '/sources/frontier')
sys.path.insert(0, _P248)
import common  # noqa: F401  (canonical path setup: caddeps + raise issue-232-final)
import fitlibF as FF
from geometry import tube
from build123d import Box, Pos, Rot, Solid
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

OUT = '/home/hatch/workspace/projects/he-piantor-ghcheck/.issue275gh-runtime'
B = 6.75
Z_EXIT = B - 1.60
Z_RUN = 2.60
EXCLUDE_PREFIX = ('tray-', 'splice-', 'shell-', 'strip-', 'Main-study-',
                  'Main-GH-')
EXCLUDE_EXACT = {'EZmate-Main-plug', 'shell-central', 'USB-reference-shell'}

def bb(s):
    b = s.bounding_box()
    return (b.min.X, b.min.Y, b.min.Z, b.max.X, b.max.Y, b.max.Z)

def bbox_gap(a, b):
    dx = max(a[0] - b[3], b[0] - a[3], 0.0)
    dy = max(a[1] - b[4], b[1] - a[4], 0.0)
    dz = max(a[2] - b[5], b[2] - a[5], 0.0)
    return math.sqrt(dx * dx + dy * dy + dz * dz)

def common_vol(a, b):
    # build123d Shape.intersect returns None (no common), a Shape, or a
    # ShapeList of solids (multi-piece common). Sum piece volumes.
    c = a.intersect(b)
    if c is None:
        return 0.0
    try:
        return float(c.volume)
    except AttributeError:
        return sum(float(s.volume) for s in c)

def extrema_dist(a, b):
    d = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
    d.Perform()
    return float(d.Value()) if d.IsDone() else -1.0

# ---------- fixed bodies ----------
raw = dict(FF.bodies_at(17, -0.60))
fixed = {}
for name, s in raw.items():
    if name.startswith(EXCLUDE_PREFIX) or name in EXCLUDE_EXACT:
        continue
    fixed[name] = s
# flipped Main component reservations: mirror X, flip Z about the face 6.75
for name, s in raw.items():
    if name.startswith('Main-study-'):
        a = bb(s)
        h = a[5] - 7.95
        fixed['flip-' + name] = Pos((-a[3] - a[0]) / 2 + 0, 0, 0) * Box(1, 1, 1)  # placeholder replaced below
        fixed['flip-' + name] = Pos(-(a[0] + a[3]) / 2, (a[1] + a[4]) / 2, B - h / 2) * Box(a[3] - a[0], a[4] - a[1], h)
# production floor slab with D-046 pocket
def slab(x0, x1, y0, y1, top):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (top - 0.5) / 2) * Box(x1 - x0, y1 - y0, top + 0.5)
fixed['floor-W'] = slab(-60, -6, -50, 62, 1.60)
fixed['floor-E'] = slab(13, 60, -50, 62, 1.60)
fixed['floor-N'] = slab(-6, 13, -50, 28, 1.60)
fixed['floor-S'] = slab(-6, 13, 48, 62, 1.60)
fixed['floor-pocket'] = slab(-6, 13, 28, 48, 0.60)

# ---------- Main GH plug envelopes (Rev.10 sites, underside) ----------
def plug_envelope(centre, rowdir, outward):
    ang = math.degrees(math.atan2(rowdir[1], rowdir[0]))
    cx = centre[0] + outward[0] * 3.325
    cy = centre[1] + outward[1] * 3.325
    return Pos(cx, cy, B - 4.85 / 2) * Rot(0, 0, ang) * Box(21.76, 8.15, 4.85)

SITES = {
    # outward = perpendicular to rowdir, pointing north (wire-exit side).
    # NOTE: an earlier draft had the two outward vectors swapped (each was
    # ~parallel to its own rowdir: dot ~0.997), which slid the approach
    # segments along each other and fabricated wire-wire contacts.
    # Verified: dot(rowdir, outward) ~ 0 for both sites below.
    'R': dict(centre=(24.255, 41.824), rowdir=(0.731, -0.682), outward=(-0.682, -0.731), sgn=1),
    'L': dict(centre=(-24.255, 41.824), rowdir=(0.731, 0.682), outward=(0.682, -0.731), sgn=-1),
}
plugs = {}
for side, st in SITES.items():
    plugs[f'plug-main-{side}'] = plug_envelope(st['centre'], st['rowdir'], st['outward'])
plugs['plug-wing-R'] = raw['underside-right-J_WING']
plugs['plug-wing-L'] = raw['underside-left-J_WING']

# ---------- wires ----------
def wire_pts(side, k):
    # Route v2 (after v1 audit): bundle pitch 1.30; the bundle->approach turn
    # is a cubic-Bezier fan (tangent +Y at the bundle end, tangent -outward
    # at F) sampled at 6 interior points, so the transverse spacing rotates
    # gradually instead of skewing two straight segments together (v1's
    # straight climbs converged to 0.50 mm centrelines). The approach then
    # runs LOW at Z_RUN until 3 mm from the row and rises only in the last
    # 2 mm of plan distance (v1 rose to 4.30 at 13 mm out and its L14 wire
    # grazed the flipped C27 reservation, which hangs to Z 3.75).
    st = SITES[side]
    sgn = st['sgn']
    u = (k - 7.5) * 1.25
    wx = sgn * 27 + (k - 7.5) * 1.25
    bx = sgn * 26 + (k - 7.5) * 1.30
    rp = (st['centre'][0] + st['rowdir'][0] * u, st['centre'][1] + st['rowdir'][1] * u)
    J = (rp[0] + st['outward'][0] * 9.0, rp[1] + st['outward'][1] * 9.0, Z_RUN)
    W = (rp[0] + st['outward'][0] * 3.5, rp[1] + st['outward'][1] * 3.5, Z_RUN)
    M = (rp[0] + st['outward'][0] * 1.0, rp[1] + st['outward'][1] * 1.0, Z_EXIT)
    S = (bx, 8.0, Z_RUN)
    # Fan v10: rotating frame over the WHOLE run from the Wing-exit drop
    # (Y -13) to J, pitch bump 1.30 -> ~1.65 -> 1.25. Diagnosis of v1-v9:
    # two multiplicative squeezes - (a) perpendicular factor: heading
    # swings south -> SSW -> SSE while spacing rotates to rowdir, passing
    # within ~25 deg of it (factor ~0.6 at pitch 1.3); (b) radius factor:
    # the turn concentrated in ~30 mm gives centre radius ~15 mm vs
    # offsets +-11 mm, scaling inner spacing by ~(R-d)/R ~ 0.4. Cure for
    # (b) is LENGTH: distributing the same ~110 deg of heading change
    # over the full ~48 mm run raises R to ~25-30 mm. Centre path = cubic
    # Bezier (tangent +Y at (sgn*26, -13), -outward at Jc), arc-length
    # resampled; beta and pitch follow the Bezier parameter.
    Jc = (st['centre'][0] + st['outward'][0] * 9.0, st['centre'][1] + st['outward'][1] * 9.0)
    C0 = (sgn * 26.0, -13.0)
    C1 = (sgn * 26.0, 8.0)
    C2 = (Jc[0] + st['outward'][0] * 10.0, Jc[1] + st['outward'][1] * 10.0)
    C3 = Jc
    beta_end = math.atan2(st['rowdir'][1], st['rowdir'][0])
    dense = []
    for i in range(201):
        w = i / 200
        dense.append((w,
                      (1 - w) ** 3 * C0[0] + 3 * (1 - w) ** 2 * w * C1[0] +
                      3 * (1 - w) * w * w * C2[0] + w ** 3 * C3[0],
                      (1 - w) ** 3 * C0[1] + 3 * (1 - w) ** 2 * w * C1[1] +
                      3 * (1 - w) * w * w * C2[1] + w ** 3 * C3[1]))
    cum = [0.0]
    for i in range(1, len(dense)):
        cum.append(cum[-1] + math.hypot(dense[i][1] - dense[i - 1][1],
                                        dense[i][2] - dense[i - 1][2]))
    picks = []
    target = 4.6
    for i in range(1, len(dense) - 1):
        if cum[i] >= target:
            picks.append(dense[i])
            target = cum[i] + 4.6
    if picks and cum[-1] - cum[dense.index(picks[-1])] < 3.4:
        picks.pop()
    # Two-level fan: alternate wires ride +1.0 mm in Z through the fan
    # (fading in/out with sin^2 so both plug rows stay planar). Where the
    # plan spacing dips to ~0.6 mm mid-turn, the vertical offset restores
    # the 3D distance to >= 1.0 mm. Headroom: fan top 4.10 vs flipped
    # Main underside 6.75 (components in this region bottom at >= 4.25
    # real / audited below). Same-parity pairs (k, k+2) share a level;
    # their plan spacing is ~2x pitch and was clean in the planar runs.
    fan = [(bx, -13.0, Z_RUN)]
    for w, cx, cy in picks:
        s = w * w * (3 - 2 * w)
        beta = beta_end * s
        pitch = 1.30 + (1.25 - 1.30) * s + 0.50 * math.sin(math.pi * w) ** 2
        off = (k - 7.5) * pitch
        fw = min(1.0, max(0.0, (w - 0.22) / 0.82))
        dz = (1.15 if k % 2 == 1 else 0.0) * math.sin(math.pi * fw) ** 2
        fan.append((cx + off * math.cos(beta), cy + off * math.sin(beta),
                    Z_RUN + dz))
    fan.append(J)
    return [(wx, -34.5, Z_EXIT), (wx, -27.0, 4.30)] + fan + [W, M]

wires, lengths, centrelines = {}, {}, {}
wire_validity = {}
for side in 'RL':
    st = SITES[side]
    assert abs(st['rowdir'][0] * st['outward'][0] + st['rowdir'][1] * st['outward'][1]) < 0.01, f'rowdir/outward not perpendicular at {side}'
    for k in range(1, 15):
        pts = wire_pts(side, k)
        centrelines[f'{side}{k}'] = pts
        solid, path = tube([list(p) for p in pts], 0.5)
        wires[f'{side}{k}'] = solid
        lengths[f'{side}{k}'] = float(path.length)
        expect = math.pi * 0.25 * lengths[f'{side}{k}']
        wire_validity[f'{side}{k}'] = dict(valid=bool(solid.is_valid),
                                           vol=round(float(solid.volume), 2),
                                           vol_expect=round(expect, 2))
assert all(v['valid'] and abs(v['vol'] - v['vol_expect']) < 0.5 for v in wire_validity.values()), 'wire solid validation failed'

# ---------- plan-view crossing count ----------
def seg_int(p1, p2, p3, p4):
    def cr(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    d1, d2, d3, d4 = cr(p3, p4, p1), cr(p3, p4, p2), cr(p1, p2, p3), cr(p1, p2, p4)
    return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)) and d1 != 0 and d2 != 0 and d3 != 0 and d4 != 0

crossings = []
names = list(centrelines)
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        A = [(p[0], p[1]) for p in centrelines[names[i]]]
        Bp = [(p[0], p[1]) for p in centrelines[names[j]]]
        hit = any(seg_int(A[m], A[m + 1], Bp[n], Bp[n + 1]) for m in range(len(A) - 1) for n in range(len(Bp) - 1))
        if hit:
            crossings.append((names[i], names[j]))

# ---------- audit ----------
fixed_bb = {n: bb(s) for n, s in fixed.items()}
plug_bb = {n: bb(s) for n, s in plugs.items()}
contacts, near = [], []
def audit_pair(a_name, a, a_bb, b_name, b, b_bb, kind):
    g = bbox_gap(a_bb, b_bb)
    if g > 0.6:
        return
    v = common_vol(a, b)
    if v > 1e-6:
        contacts.append(dict(kind=kind, a=a_name, b=b_name, volume_mm3=round(v, 4)))
    elif g < 0.5:
        d = extrema_dist(a, b)
        near.append(dict(kind=kind, a=a_name, b=b_name, bbox_gap=round(g, 3), min_dist=round(d, 3)))

wire_bb = {n: bb(s) for n, s in wires.items()}
for wn, w in wires.items():
    side = wn[0]
    for fn, f in fixed.items():
        audit_pair(wn, w, wire_bb[wn], fn, f, fixed_bb[fn], 'wire-fixed')
    for pn, p in plugs.items():
        if pn.endswith('-' + side):
            continue
        audit_pair(wn, w, wire_bb[wn], pn, p, plug_bb[pn], 'wire-plug')
SELF_BODY = {'plug-wing-R': 'underside-right-J_WING', 'plug-wing-L': 'underside-left-J_WING'}
for pn, p in plugs.items():
    for fn, f in fixed.items():
        if SELF_BODY.get(pn) == fn:
            continue  # the Wing plug envelope IS this library body
        audit_pair(pn, p, plug_bb[pn], fn, f, fixed_bb[fn], 'plug-fixed')
wl = list(wires)
for i in range(len(wl)):
    for j in range(i + 1, len(wl)):
        audit_pair(wl[i], wires[wl[i]], wire_bb[wl[i]], wl[j], wires[wl[j]], wire_bb[wl[j]], 'wire-wire')

# ---------- self-test + Q1-at-10.90 quantification ----------
test_wire = wires['R1'].translate((0, 0, -3.0))
self_test_vol = common_vol(test_wire, fixed['floor-E'])
plug1090 = raw['underside-right-J_WING'].translate((0, 0, -2.05))
q1_vol = common_vol(plug1090, fixed['floor-E']) + common_vol(plug1090, fixed['floor-N'])

res = dict(
    plate_top=12.95, B=B,
    wire_validity=wire_validity,
    spot_extrema_R1_R2=round(extrema_dist(wires['R1'], wires['R2']), 3),
    n_fixed_bodies=len(fixed), n_wires=len(wires),
    plan_crossings=crossings,
    contacts=contacts, near_pairs=near,
    lengths_mm={k: round(v, 2) for k, v in lengths.items()},
    max_length_mm=round(max(lengths.values()), 2),
    self_test_floor_contact_mm3=round(self_test_vol, 3),
    q1_plug_floor_intersection_at_plate_10_90_mm3=round(q1_vol, 3),
)
json.dump(res, open(f'{OUT}/audit-1295-wireside.json', 'w'), indent=1)
print('contacts:', len(contacts))
for c in contacts: print('  ', c)
print('plan crossings:', crossings)
print('max length:', res['max_length_mm'])
print('self-test (must be >0):', res['self_test_floor_contact_mm3'])
print('Q1 plug/floor intersection at 10.90 (must be >0):', res['q1_plug_floor_intersection_at_plate_10_90_mm3'])
print('near pairs (dist<0.5, no contact):', len(near))
for n in near[:20]: print('  ', n)
