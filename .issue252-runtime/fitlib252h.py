"""Height-stepped variant of fitlib252 (S4): the whole above-floor
assembly translates +s in Z (s = plate_top - 13.55); trays/floor use
the frontier fitlibF SHIFT/EXTEND/FIXED classification; the carrier
board/headers translate +s; seat posts extend from the floor."""
import sys
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-midconn/.issue252-runtime')
import fitlib252 as C
_ORIG_SEG = C.seg_points  # captured before any monkeypatching
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
import fitlibF as FF
from build123d import Box, Cylinder, Pos

def seg_points_s(D, i, side, s):
    wp, mp = _ORIG_SEG(D, i, side)
    if s == 0: return wp, mp
    return ([[p[0], p[1], p[2] + s] for p in wp],
            [[p[0], p[1], p[2] + s] for p in mp])

def carrier_bodies_s(side, s):
    out = []
    for n, solid in C.carrier_bodies(side):
        if n.startswith('seat-'):
            # rebuild post extended: cylinder from floor to board bottom
            px, py = C.POSTS[0] if 'post0' in n else C.POSTS[1]
            if side == 'left': px = -px
            h = 12.75 + s
            out.append((n, Pos(px, py, h / 2) * Cylinder(3.5, h)))
        else:
            out.append((n, Pos(0, 0, s) * solid))
    return out

def bodies_at(s):
    bodies = {}
    for p in (17, 16):
        bl = list(FF.bodies_at(p, s))
        bl += carrier_bodies_s('right', s) + carrier_bodies_s('left', s)
        bodies[p] = bl
    return bodies

def build_all_s(D, s):
    import repair18_lib as R
    import routes_round17 as rr
    import fitlib18 as F
    wires, lens, failed = {}, {}, []
    for side in ('right', 'left'):
        for i in range(14):
            wp, mp = seg_points_s(D, i, side, s)
            for seg, pts, un in (('SegW', wp, 7.30), ('SegM', mp, 6.80)):
                nm = C.wire_name(seg, side, i)
                pts2 = rr.split_corners(pts)
                r, why = R.build_s(pts2)
                if r is None:
                    failed.append((nm, why)); continue
                w, L = F.build_wire(pts2)
                wires[nm] = r
                lens[nm] = round(L + un, 2)
    return wires, lens, failed
