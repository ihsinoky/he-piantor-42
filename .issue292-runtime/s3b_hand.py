"""S3b hand-planned legs for the remaining unconnected pairs.
Each job: route on a chosen layer from a known point (escape via /
B-end / pad) to a named far item (nearest item to an approx point),
with explicit via points searched near given locations for two-leg
jobs. Reuses s3b_merge5 machinery (cached indices, shape A*)."""
import pcbnew as p, math
from shapely.geometry import Point, LineString
from pathlib import Path
src = open('s3b_merge5.py').read().split('total_added = 0')[0]
g = {}
exec(src, g)
items, b = g['items'], g['b']
add_track, add_via, astar = g['add_track'], g['add_via'], g['astar']
via_legal, simplify, extend = g['via_legal'], g['simplify'], g['extend']
BPATH = g['BPATH']

def nearest_item(net, approx, exclude_pts):
    best = None
    for it in items[net]:
        for pt in it['pts']:
            if any(abs(pt[0]-e[0]) < 0.01 and abs(pt[1]-e[1]) < 0.01 for e in exclude_pts):
                continue
            d = math.hypot(pt[0]-approx[0], pt[1]-approx[1])
            if best is None or d < best[0]: best = (d, it, pt)
    return best[1], best[2]

def find_via(net, near, r=2.5):
    cands = []
    x = near[0] - r
    while x <= near[0] + r:
        y = near[1] - r
        while y <= near[1] + r:
            if via_legal(net, round(x, 2), round(y, 2)):
                cands.append((math.hypot(x-near[0], y-near[1]), (round(x, 2), round(y, 2))))
            y += 0.1
        x += 0.1
    cands.sort()
    return cands[0][1] if cands else None

def leg(net, frm, Lr, target_item, w, via_at_end=False):
    """Route on Lr from point frm (must be on Lr or on a via) to
    target_item's shape. Optionally place a via at the target's
    nearest endpoint (when the item is not on Lr)."""
    seed = Point(*frm).buffer(0.3 + w/2) if via_at_end is None else Point(*frm).buffer(w/2)
    goal = target_item['shape'].buffer(w/2)
    path = astar(net, Lr, seed, goal, w)
    if not path: return False
    path = extend(simplify(path))
    for i in range(len(path) - 1): add_track(net, *path[i], *path[i+1], w, Lr)
    return True

def route_to(net, frm, Lr, approx, w):
    it, pt = nearest_item(net, approx, [frm])
    layers = [Lr] + [L for L in ('I2', 'B', 'F') if L != Lr]
    for L in layers:
        if L not in it['layers'] and L != Lr:
            continue  # only the requested layer may need an end via
        ok = leg(net, frm, L, it, w)
        print(net, 'leg', L, '->', pt, 'OK' if ok else 'FAIL')
        if ok: return ok, it, pt
    return False, it, pt

def two_leg(net, frm, via_near, Lr1, Lr2, approx, w):
    it, pt = nearest_item(net, approx, [frm])
    vp = find_via(net, via_near)
    if not vp:
        print(net, 'no via near', via_near); return False
    # leg1 on Lr1 from frm to the via point
    ok1 = leg(net, frm, Lr1, {'shape': Point(*vp).buffer(0.3)}, w)
    if not ok1:
        print(net, 'leg1 FAIL'); return False
    add_via(net, *vp)
    # leg2 on Lr2 from via to target; if target not on Lr2, via at end
    if Lr2 in it['layers']:
        ok2 = leg(net, vp, Lr2, it, w)
    else:
        ok2 = leg(net, vp, Lr2, {'shape': Point(*pt).buffer(0.3)}, w)
        if ok2: add_via(net, *pt)
    print(net, 'two-leg via', vp, '->', pt, 'OK' if ok2 else 'FAIL')
    return ok2

# --- jobs ---
# GND bridge inside the field (w 0.2, field class)
it, pt = nearest_item('GND', (76.55, 125.05), [(77.5, 124.8)])
ok = leg('GND', (77.5, 124.8), 'F', it, 0.2)
print('GND bridge', 'OK' if ok else 'FAIL')
# USB_DP: escape via -> I2 track NE
route_to('USB_DP', (69.6, 125.8), 'I2', (90.7, 108.1), 0.1)
# VBUS: escape via -> B track N (w 0.3)
route_to('VBUS', (80.6, 125.9), 'B', (86.25, 111.5), 0.3)
# PAD_DR: escape via -> B track N
route_to('PAD_DR', (76.0, 119.35), 'B', (78.8, 112.4), 0.1)
# PAD_SDA: escape via -> B track NE
route_to('PAD_SDA', (79.1, 119.35), 'B', (93.8, 103.3), 0.1)
# VBAT_GATE_M: escape via -> B track far E
route_to('VBAT_GATE_M', (78.1, 119.35), 'B', (116.5, 127.3), 0.1)
# SWDCLK: escape via -> F track SE
route_to('SWDCLK', (80.6, 124.3), 'F', (91.1, 133.5), 0.1)
b.Save(str(BPATH)); print('saved batch 1')

# --- batch 2 (appended): ADC_C forced I2 ---
src2 = open('s3b_merge5.py').read().split('total_added = 0')[0]
