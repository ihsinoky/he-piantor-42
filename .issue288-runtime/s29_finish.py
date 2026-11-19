"""S2.4c finish pass: multi-strategy component connection + pad escapes.

Phase 1: for each split net try, in order, nearest-point pair, pad-centre
pairs (nearest first), pad-to-segment-endpoint pairs; route the first
success; rebuild components after each success.
Phase 2: for a net still split with a singleton PAD component (the pad is
in a sealed pocket for the grid router), place a scripted escape: F track
east from the pad, via at the first legal landing in a scan box, short
B stub anchor. Then back to phase 1.
DRC arbitrates after the pass (s28 step1 cleans any marginal segments).
"""
import math
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, add_route, route, _seg_clear
from s28_component_route import Comp, POWER_NETS

WT = Path('/home/hatch/workspace/projects/he-piantor-wmatrix')
TREE = WT / 'hardware/kicad/qualification/issue-288-wmatrix'
BOARD = TREE / 'wmatrix.kicad_pcb'
MM = 1e6


def item_points(comp, idxs, kinds):
    pts = []
    for i in idxs:
        it = comp.items[i]
        if it['kind'] not in kinds:
            continue
        if it['kind'] == 'seg':
            pts.append((it['ax'], it['ay'], 0 if it['layers'][0] else 1))
            pts.append((it['bx'], it['by'], 0 if it['layers'][0] else 1))
        else:
            pts.append((it['x'], it['y'], 0))
    return pts


def try_connect(b, obs, comp, net, comps):
    """Try to connect the two closest components of `net`. Returns True."""
    netobj = b.FindNet(net)
    nc = netobj.GetNetCode()
    width = 0.30 if net in POWER_NETS else 0.10
    # candidate component pairs by nearest-point distance
    pairs = []
    for ii in range(len(comps)):
        for jj in range(ii + 1, len(comps)):
            r = comp.nearest_pair(comps[ii], comps[jj])
            if r:
                pairs.append((r[0], ii, jj, r))
    pairs.sort(key=lambda t: t[0])
    for _, ii, jj, r in pairs[:2]:
        if r[0] < 0.05:
            return True  # coincident copper: DRC-connected already
        res = route(obs, r[1], r[2], nc, width)
        if res:
            print(f'  connected {net} (nearest)', flush=True)
            add_route(b, netobj, width, res[0], res[1])
            register(obs, res, width, nc)
            return True
    # pad-centre pairs
    for _, ii, jj, _r in pairs[:2]:
        pa = item_points(comp, comps[ii], ('pad',))
        pb = item_points(comp, comps[jj], ('pad',))
        cand = sorted(((math.hypot(a[0] - c[0], a[1] - c[1]), a, c) for a in pa for c in pb),
                      key=lambda t: t[0])
        for _, a, c in cand[:8]:
            print(f'  try {net} padpair', flush=True)
            res = route(obs, a, c, nc, width)
            if res:
                add_route(b, netobj, width, res[0], res[1])
                register(obs, res, width, nc)
                return True
        # pad to segment endpoints
        ea = item_points(comp, comps[ii], ('pad', 'seg'))
        eb = item_points(comp, comps[jj], ('pad', 'seg'))
        cand = sorted(((math.hypot(a[0] - c[0], a[1] - c[1]), a, c) for a in ea for c in eb),
                      key=lambda t: t[0])
        for _, a, c in cand[:8]:
            print(f'  try {net} padpair', flush=True)
            res = route(obs, a, c, nc, width)
            if res:
                add_route(b, netobj, width, res[0], res[1])
                register(obs, res, width, nc)
                return True
    return False


def register(obs, res, width, nc):
    points, vias = res
    for (ax, ay, al), (bx, by, bl) in zip(points, points[1:]):
        if al == bl:
            obs.add_seg(ax, ay, bx, by, width / 2, nc, al)
    for (vx, vy) in vias:
        obs.add_via(vx, vy, 0.30, nc)


def escape_pad(b, obs, net, pad_item):
    """Scripted escape for a pocketed singleton pad. Returns True on success.

    Scan a box around the pad for legal via landings (nearest first);
    for each, try path shapes: direct segment, or two-segment via a
    stub point (S/E/W/N). First fully-clear shape wins; a 1mm B stub
    anchors the escaped component in open space.
    """
    netobj = b.FindNet(net)
    nc = netobj.GetNetCode()
    width = 0.30 if net in POWER_NETS else 0.10
    px, py = pad_item['x'], pad_item['y']
    landings = []
    vy = py - 1.5
    while vy <= py + 5.0:
        vx = px - 2.5
        while vx <= px + 3.5:
            if not (obs.blocked(vx, vy, 0, nc, 0.30, via=True) or
                    obs.blocked(vx, vy, 1, nc, 0.30, via=True)):
                landings.append((math.hypot(vx - px, vy - py), vx, vy))
            vx += 0.25
        vy += 0.25
    landings.sort()
    stubs = [(px, py + 1.5), (px + 1.25, py), (px - 1.25, py), (px, py - 1.0)]
    for _, vx, vy in landings[:60]:
        shapes = [[(px, py, 0), (vx, vy, 0)]]
        for (sx, sy) in stubs:
            shapes.append([(px, py, 0), (sx, sy, 0), (vx, vy, 0)])
        for pts in shapes:
            if all(_seg_clear(obs, a[0], a[1], c[0], c[1], 0, nc, width / 2)
                   for a, c in zip(pts, pts[1:])):
                add_route(b, netobj, width, pts, [(vx, vy)])
                add_route(b, netobj, width, [(vx, vy, 1), (vx, vy + 1.0, 1)], [])
                for a, c in zip(pts, pts[1:]):
                    obs.add_seg(a[0], a[1], c[0], c[1], width / 2, nc, 0)
                obs.add_via(vx, vy, 0.30, nc)
                obs.add_seg(vx, vy, vx, vy + 1.0, width / 2, nc, 1)
                print(f'  escape {net} pad ({px:.2f},{py:.2f}) via ({vx:.2f},{vy:.2f})', flush=True)
                return True
    return False


def main():
    for round_ in range(8):
        b = pcbnew.LoadBoard(str(BOARD))
        comp = Comp(b)
        obs = Obstacles(b)
        nets = sorted({it['net'] for it in comp.items if it['net']})
        progress = False
        # phase A: escapes for singleton pads of split nets
        for net in nets:
            comps = comp.components(net)
            if len(comps) <= 1:
                continue
            singles = [c for c in comps if len(c) == 1 and comp.items[c[0]]['kind'] == 'pad']
            for c in singles:
                if escape_pad(b, obs, net, comp.items[c[0]]):
                    progress = True
                    comp = Comp(b)
                    obs = Obstacles(b)
        # phase B: tries
        for net in nets:
            comps = comp.components(net)
            if len(comps) <= 1:
                continue
            if try_connect(b, obs, comp, net, comps):
                progress = True
                comp = Comp(b)
                obs = Obstacles(b)
        b.Save(str(BOARD))
        comp = Comp(b)
        split = {n: len(comp.components(n)) for n in nets if len(comp.components(n)) > 1}
        print(f'round {round_}: split nets {split}', flush=True)
        if not split:
            break
        if not progress:
            print('no progress - stopping')
            break


if __name__ == '__main__':
    main()
