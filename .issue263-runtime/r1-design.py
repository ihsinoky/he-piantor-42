"""R1 notch design: fit the required cut region's inner boundary to a line,
build a clean notch profile (horizontal entries + slanted floor + R1.0
fillets at the floor corners), verify coverage of the required region.
Board frame per variant. Output: r1-notch-design.json"""
import sys, json
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/geometry/lib/python3.12/site-packages')
import numpy as np
from shapely.geometry import Polygon, LineString, Point
from shapely.affinity import rotate as shp_rotate, translate as shp_translate
from shapely.ops import unary_union

RT = '/home/hatch/workspace/projects/he-piantor-boards/.issue263-runtime'
req = json.load(open(f'{RT}/r1-notch.json'))
wj = json.load(open(f'{RT}/r1-wings.json'))
bj = json.load(open(f'{RT}/f2-board.json'))

def to_case(pts):
    return [(x - 100.0, y - 70.0) for x, y in pts]

old_poly = Polygon(to_case(bj['outline_rev7']))
new_poly = Polygon(to_case(bj['outline_rev8']))
tab = new_poly.difference(old_poly)

design = {}
for name, env, deg in (('wing-rev5-16mm-right', (27.0, -37.5), -30.5),
                       ('wing-rev5-16mm-left', (-27.0, -37.5), 30.5),
                       ('wing-rev5-17mm-right', (27.0, -37.5), -30.5),
                       ('wing-rev5-17mm-left', (-27.0, -37.5), 30.5)):
    d = wj[name]
    jx, jy = d['jw_pos']
    wing_board = Polygon(d['outline'])
    wx = wing_board.bounds[0]  # west edge x
    req_poly = unary_union([Polygon(p) for p in req[name]['notch_board']])
    # inner boundary points: vertices at least 1.0 mm east/west of the edge
    # (for left boards the west edge is the MAX x side)
    right = 'right' in name
    edge_x = wing_board.bounds[0] if right else wing_board.bounds[2]
    pts = np.array(req_poly.exterior.coords)
    if right:
        inner = pts[pts[:, 0] > edge_x + 1.0]
    else:
        inner = pts[pts[:, 0] < edge_x - 1.0]
    # fit x = a*y + b on the long slanted run (exclude cap arcs: keep points
    # whose y is within the middle 70% of the inner-point y range)
    ys = inner[:, 1]
    lo, hi = np.percentile(ys, [15, 85])
    mid = inner[(ys >= lo) & (ys <= hi)]
    a, b = np.polyfit(mid[:, 1], mid[:, 0], 1)
    resid = np.abs(mid[:, 0] - (a * mid[:, 1] + b)).max()
    y_lo, y_hi = ys.min() - 0.6, ys.max() + 0.6
    # floor line pushed 0.15 mm further into the board from required region
    push = 0.15 if right else -0.15
    b2 = b + push
    x_top = a * y_hi + b2
    x_bot = a * y_lo + b2
    # notch polygon (sharp corners first), then fillet via buffer trick:
    # erode/dilate is wrong for fillets; build with arcs manually using
    # shapely: polygon minus corner triangles replaced by arc approx -
    # simpler: build profile points with arc sampling at B and C (R=1.0).
    R = 1.0
    # corners: B=(x_top,y_hi) C=(x_bot,y_lo); entry corners at edge are
    # square (convex from board side? entry is concave too - the profile
    # turns 90deg at the edge; those corners are RE-ENTRANT from the
    # material side? No: at the edge, material is east of profile going
    # south... The two edge corners are convex (board material corner),
    # the two floor corners are concave (need fillet R>=1 for routing).
    # Arc centres for floor corners: offset R along both segments.
    import math
    def fillet_pts(P, Pprev, Pnext, R, n=6):
        v1 = np.array(Pprev) - np.array(P); v1 = v1 / np.linalg.norm(v1)
        v2 = np.array(Pnext) - np.array(P); v2 = v2 / np.linalg.norm(v2)
        t1 = np.array(P) + v1 * R / math.tan(math.acos(np.clip(np.dot(v1, v2), -1, 1)) / 2) * 1.0
        # tangent length for fillet radius R: t = R / tan(theta/2)
        theta = math.acos(np.clip(np.dot(v1, v2), -1, 1))
        t = R / math.tan(theta / 2)
        t1 = np.array(P) + v1 * t
        t2 = np.array(P) + v2 * t
        c = np.array(P) + (v1 + v2) / np.linalg.norm(v1 + v2) * (R / math.sin(theta / 2))
        a1 = math.atan2(t1[1] - c[1], t1[0] - c[0])
        a2 = math.atan2(t2[1] - c[1], t2[0] - c[0])
        # sweep the short way
        while a2 - a1 > math.pi: a2 -= 2 * math.pi
        while a2 - a1 < -math.pi: a2 += 2 * math.pi
        return [tuple(c + R * np.array([math.cos(a1 + (a2 - a1) * i / n),
                                        math.sin(a1 + (a2 - a1) * i / n)])) for i in range(n + 1)]
    A = (edge_x, y_hi); B = (x_top, y_hi); C = (x_bot, y_lo); D = (edge_x, y_lo)
    prof = [A]
    prof += fillet_pts(B, A, C, R)[:-1]
    prof += fillet_pts(C, B, D, R)
    prof += [D]
    notch_poly = Polygon(prof + [(edge_x - (2 if right else -2), y_lo),
                                 (edge_x - (2 if right else -2), y_hi)])
    covers = notch_poly.contains(req_poly) or notch_poly.covers(req_poly)
    # new outline + case-frame clearance check
    new_outline = wing_board.difference(notch_poly)
    nb = shp_translate(shp_rotate(Polygon([(x - jx, y - jy) for x, y in new_outline.exterior.coords]),
                                  deg, origin=(0, 0)), xoff=env[0], yoff=env[1])
    dist = nb.distance(tab)
    design[name] = dict(edge_x=edge_x, y_lo=round(y_lo, 3), y_hi=round(y_hi, 3),
                        floor_line=[round(a, 5), round(b2, 3)], fit_resid_mm=round(float(resid), 4),
                        profile=[[round(x, 3), round(y, 3)] for x, y in prof],
                        covers_required=bool(covers), case_dist_to_tab=round(dist, 3),
                        removed_area=round(notch_poly.intersection(wing_board).area, 2))
    print(f"{name}: fit resid {resid:.3f} mm; notch y {y_lo:.2f}..{y_hi:.2f}; "
          f"covers={covers}; dist(new outline, tab)={dist:.3f} mm; "
          f"removed {notch_poly.intersection(wing_board).area:.1f} mm2", flush=True)
json.dump(design, open(f'{RT}/r1-notch-design.json', 'w'), indent=1)
print('done')
