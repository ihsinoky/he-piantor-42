"""Issue #270 stage 1: geometry extraction to case frame.

Frames (exactly as the #263 F2/R3 verification):
- Main case = board - (100, 70).
- Wing case = shapely-rotate(board - J_WING origin, +30.5 L / -30.5 R)
  + envelope centre (-27,-37.5) L / (27,-37.5) R.   [r3-seam.py]
- Pad clearance yardstick = pad axis-aligned BBox corners vs outline
  (build-main2.py method; reproduces REPORT worst 0.7241).
Outputs geometry.json + validation prints.
"""
import json, math
from pathlib import Path
import pcbnew as p
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union, polygonize
from shapely.affinity import rotate as shp_rotate, translate as shp_translate

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
Q263 = ROOT / 'hardware/kicad/qualification/issue-263-implementation'
MM = 1e6


def xy(v):
    return [p.ToMM(v.x), p.ToMM(v.y)]


def outline_of(board):
    segs = []
    for d in board.GetDrawings():
        if d.GetLayer() == p.Edge_Cuts:
            segs.append(LineString([xy(d.GetStart()), xy(d.GetEnd())]))
    polys = list(polygonize(unary_union(segs)))
    polys.sort(key=lambda q: -q.area)
    return [list(c) for c in polys[0].exterior.coords]


def main_case(pt):
    return (pt[0] - 100.0, pt[1] - 70.0)


def pad_bbox_corners(pad):
    bb = pad.GetBoundingBox()
    return [(bb.GetLeft() / MM, bb.GetTop() / MM), (bb.GetRight() / MM, bb.GetTop() / MM),
            (bb.GetLeft() / MM, bb.GetBottom() / MM), (bb.GetRight() / MM, bb.GetBottom() / MM)]


def pad_true_corners(pad):
    c = pad.GetPosition()
    cx, cy = c.x / MM, c.y / MM
    s = pad.GetSize()
    w, h = s.x / MM, s.y / MM
    th = -math.radians(pad.GetOrientationDegrees())
    co, si = math.cos(th), math.sin(th)
    return [(cx + dx * co - dy * si, cy + dx * si + dy * co)
            for dx, dy in ((w / 2, h / 2), (w / 2, -h / 2), (-w / 2, -h / 2), (-w / 2, h / 2))]


out = {}

# ---------- Main ----------
b = p.LoadBoard(str(Q263 / 'main-rev8/main.kicad_pcb'))
main_outline = [list(main_case(c)) for c in outline_of(b)]
out['main_rev8_outline'] = main_outline
b7 = p.LoadBoard(str(ROOT / 'hardware/kicad/qualification/issue-240-main-rev7/inspection/final/main.kicad_pcb'))
out['main_rev7_outline'] = [list(main_case(c)) for c in outline_of(b7)]

pads = {}
for ref in ('J2', 'J3'):
    f = [x for x in b.GetFootprints() if x.GetReference() == ref][0]
    lst = []
    for pad in f.Pads():
        lst.append(dict(num=pad.GetNumber(),
                        bbox=[list(main_case(c)) for c in pad_bbox_corners(pad)],
                        corners=[list(main_case(c)) for c in pad_true_corners(pad)],
                        centre=list(main_case(xy(pad.GetPosition())))))
    pads[ref] = lst
out['main_zif_pads'] = pads

WIN = {'J2': (56, 91, 104, 134), 'J3': (106, 91, 144, 134)}


def in_win(x, y, w):
    return w[0] <= x <= w[2] and w[1] <= y <= w[3]


copper = []
for tr in b.GetTracks():
    s, e = xy(tr.GetStart()), xy(tr.GetEnd())
    for name, w in WIN.items():
        if in_win(s[0], s[1], w) or in_win(e[0], e[1], w):
            if isinstance(tr, p.PCB_VIA):
                dia = max(tr.GetWidth(p.F_Cu), tr.GetWidth(p.B_Cu)) / MM
                copper.append(dict(kind='via', zone=name, centre=list(main_case(s)), dia=dia))
            else:
                copper.append(dict(kind='track', zone=name, a=list(main_case(s)), b=list(main_case(e)),
                                   width=tr.GetWidth() / MM))
            break
for f in b.GetFootprints():
    for pad in f.Pads():
        pos = xy(pad.GetPosition())
        for name, w in WIN.items():
            if in_win(pos[0], pos[1], w):
                copper.append(dict(kind='pad', zone=name, ref=f.GetReference(), num=pad.GetNumber(),
                                   corners=[list(main_case(c)) for c in pad_true_corners(pad)]))
                break
out['main_copper_near_tabs'] = copper

# ---------- Wings (F2/R3 transform) ----------
wings = {}
for side, deg, env in (('left', 30.5, (-27.0, -37.5)), ('right', -30.5, (27.0, -37.5))):
    wb = p.LoadBoard(str(Q263 / f'wing-rev5-17mm-{side}/main.kicad_pcb'))
    jf = [x for x in wb.GetFootprints() if x.GetReference() == 'J_WING'][0]
    jx, jy = xy(jf.GetPosition())

    def xf(pt, jx=jx, jy=jy, deg=deg, env=env):
        q = shp_rotate(Point(pt[0] - jx, pt[1] - jy), deg, origin=(0, 0))
        return (q.x + env[0], q.y + env[1])

    base = Polygon([(x - jx, y - jy) for x, y in outline_of(wb)])
    wpoly = shp_translate(shp_rotate(base, deg, origin=(0, 0)), xoff=env[0], yoff=env[1])
    keys = []
    for f in wb.GetFootprints():
        if f.GetReference().startswith(('U_HA', 'U_HB', 'U_HC')):
            keys.append(list(xf(xy(f.GetPosition()))))
    jw = {pad.GetNumber(): list(xf(xy(pad.GetPosition()))) for pad in jf.Pads()}
    wings[side] = dict(outline=[list(c) for c in wpoly.exterior.coords], keys=keys, jwing=jw,
                       jw_pos_board=[jx, jy])
out['wings'] = wings

(HERE / 'geometry.json').write_text(json.dumps(out))

# ---------- validation ----------
mp = Polygon(main_outline)
print('main outline pts', len(main_outline), 'area', round(mp.area, 1))
for side in ('left', 'right'):
    wp = Polygon(wings[side]['outline'])
    print(f'wing {side}: seam {mp.distance(wp):.4f} (REPORT 0.5215 L / 0.5221 R), '
          f'overlap {mp.intersection(wp).area:.4f}, keys {len(wings[side]["keys"])}, '
          f'pin1 {wings[side]["jwing"]["1"]}, pin14 {wings[side]["jwing"]["14"]}')
worst = 1e9
for ref, lst in pads.items():
    for pd in lst:
        for c in pd['bbox']:
            worst = min(worst, mp.exterior.distance(Point(c)))
print('worst ZIF pad bbox-corner clearance (current):', round(worst, 4), '(REPORT 0.7241)')
print('copper items near tabs:', len(copper))
