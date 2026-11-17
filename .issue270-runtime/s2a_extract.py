"""Issue #270 stage 2a: Wing variant extraction (16+17mm, L/R).

Same fitted transform as extract.py (#263 F2/R3): rotate board about
the J_WING origin by +30.5 (L) / -30.5 (R), anchor envelope centre
at (-27,-37.5) L / (27,-37.5) R. pose-verification.json gives the
same envelope centre for 16mm and 17mm, so one transform serves both.
Outputs wing2a.json: per variant the case-frame outline, keys, and
copper items (tracks / vias / pads / courtyards) whose case-frame
bbox intersects the seam window. Validation: current seam vs the
Rev.8 Main must reproduce 0.5215 (L) / 0.5221 (R) at both pitches.
"""
import json, math
from pathlib import Path
import pcbnew as p
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union, polygonize
from shapely.affinity import rotate as shp_rotate, translate as shp_translate

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
Q263 = ROOT / 'hardware/kicad/qualification/issue-263-implementation'
MM = 1e6
g = json.loads((HERE / 'geometry.json').read_text())
main = Polygon(g['main_rev8_outline'])


def xy(v):
    return [p.ToMM(v.x), p.ToMM(v.y)]


def outline_of(board):
    segs = []
    from shapely.geometry import LineString
    for d in board.GetDrawings():
        if d.GetLayer() == p.Edge_Cuts:
            segs.append(LineString([xy(d.GetStart()), xy(d.GetEnd())]))
    polys = list(polygonize(unary_union(segs)))
    polys.sort(key=lambda q: -q.area)
    return [list(c) for c in polys[0].exterior.coords]


def pad_true_corners(pad):
    c = pad.GetPosition()
    cx, cy = c.x / MM, c.y / MM
    s = pad.GetSize()
    w, h = s.x / MM, s.y / MM
    th = -math.radians(pad.GetOrientationDegrees())
    co, si = math.cos(th), math.sin(th)
    return [(cx + dx * co - dy * si, cy + dx * si + dy * co)
            for dx, dy in ((w / 2, h / 2), (w / 2, -h / 2), (-w / 2, -h / 2), (-w / 2, h / 2))]


WIN = {'left': (-54, 12, 2, 68), 'right': (-2, 12, 54, 68)}


def in_win(pt, w, pad=2.0):
    return w[0] - pad <= pt[0] <= w[2] + pad and w[1] - pad <= pt[1] <= w[3] + pad


out = {}
for pitch in ('17mm', '16mm'):
    for side, deg, env in (('left', 30.5, (-27.0, -37.5)), ('right', -30.5, (27.0, -37.5))):
        wb = p.LoadBoard(str(Q263 / f'wing-rev5-{pitch}-{side}/main.kicad_pcb'))
        jf = [x for x in wb.GetFootprints() if x.GetReference() == 'J_WING'][0]
        jx, jy = xy(jf.GetPosition())

        def xf(pt, jx=jx, jy=jy, deg=deg, env=env):
            q = shp_rotate(Point(pt[0] - jx, pt[1] - jy), deg, origin=(0, 0))
            return (q.x + env[0], q.y + env[1])

        base = Polygon([(x - jx, y - jy) for x, y in outline_of(wb)])
        wpoly = shp_translate(shp_rotate(base, deg, origin=(0, 0)), xoff=env[0], yoff=env[1])
        w = WIN[side]
        items = []
        for tr in wb.GetTracks():
            s, e = xy(tr.GetStart()), xy(tr.GetEnd())
            cs, ce = xf(s), xf(e)
            if in_win(cs, w) or in_win(ce, w):
                if isinstance(tr, p.PCB_VIA):
                    dia = max(tr.GetWidth(p.F_Cu), tr.GetWidth(p.B_Cu)) / MM
                    items.append(dict(kind='via', centre=list(cs), dia=dia, net=tr.GetNetname()))
                else:
                    items.append(dict(kind='track', a=list(cs), b=list(ce),
                                      width=tr.GetWidth() / MM, net=tr.GetNetname()))
        for f in wb.GetFootprints():
            for pad in f.Pads():
                corners = [list(xf(c)) for c in pad_true_corners(pad)]
                cx = sum(c[0] for c in corners) / 4
                cy = sum(c[1] for c in corners) / 4
                if in_win((cx, cy), w):
                    items.append(dict(kind='pad', ref=f.GetReference(), num=pad.GetNumber(),
                                      corners=corners, net=pad.GetNetname()))
            cy_set = f.GetCourtyard(p.B_Cu)
            for i in range(cy_set.OutlineCount()):
                o = cy_set.Outline(i)
                pts = [list(xf((o.GetPoint(j).x / MM, o.GetPoint(j).y / MM))) for j in range(o.PointCount())]
                if pts and in_win(pts[0], w):
                    items.append(dict(kind='courtyard', ref=f.GetReference(), corners=pts))
        keys = []
        for f in wb.GetFootprints():
            if f.GetReference().startswith(('U_HA', 'U_HB', 'U_HC')):
                keys.append(list(xf(xy(f.GetPosition()))))
        name = f'{pitch}-{side}'
        out[name] = dict(outline=[list(c) for c in wpoly.exterior.coords], keys=keys,
                         jw_origin_board=[jx, jy], copper=items)
        print(f'{name}: seam vs Rev.8 Main {wpoly.distance(main):.4f} '
              f'(expect 0.5215 L / 0.5221 R), overlap {wpoly.intersection(main).area:.4f}, '
              f'copper items in window {len(items)}, outline area {wpoly.area:.1f}')

(HERE / 'wing2a.json').write_text(json.dumps(out))
print('saved wing2a.json')
