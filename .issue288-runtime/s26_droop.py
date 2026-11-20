"""S2.5 rail-budget gate: HALL_3V3 droop by nodal analysis on placed copper.

Graph = placed HALL_3V3_SRC + HALL_3V3 track segments and vias (both
layers). Loads: 18x TMAG5253 at ICC max 5 mA (all banks on = burst worst
case), 3x TMUX1208 at 0.1 mA, divider string 0.165 mA. Source: AP2112
VOUT pad at 3.300 V; the 0-ohm shunt is a 10 mohm edge. Copper per repo
house constants: rho 1.7241e-8 ohm*m, 35 um foil, 20 um via barrel.
Reported at nominal track width and at width-20% (house tolerance case).
Budget: <= 50 mV at the worst sensor VCC pad.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pcbnew

WT = Path('/home/hatch/workspace/projects/he-piantor-wmatrix')
TREE = WT / 'hardware/kicad/qualification/issue-288-wmatrix'
MM = 1e6
RHO = 1.7241e-8
T_CU = 35e-6
T_BARREL = 20e-6
BOARD_T = 1.2e-3


def solve(width_factor, board):
    tracks = list(board.GetTracks())
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    nets = {board.FindNet(n).GetNetCode() for n in ('HALL_3V3', 'HALL_3V3_SRC')}

    nodes = {}

    # pre-pass: collect every node key (track ends, vias, rail pads), then
    # cluster keys within 0.15 mm: router endpoints often land on a via
    # annulus or pad edge a few 0.01 mm off the centre key.
    raw_keys = set()
    for t in board.GetTracks():
        if t.GetNetCode() not in nets:
            continue
        if isinstance(t, pcbnew.PCB_VIA):
            p = t.GetPosition()
            raw_keys.add((round(p.x / MM, 3), round(p.y / MM, 3)))
        else:
            for p in (t.GetStart(), t.GetEnd()):
                raw_keys.add((round(p.x / MM, 3), round(p.y / MM, 3)))
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.GetNetCode() in nets:
                pp = p.GetPosition()
                raw_keys.add((round(pp.x / MM, 3), round(pp.y / MM, 3)))
    canon = {}
    clusters = []
    for key in sorted(raw_keys):
        placed = False
        for cl in clusters:
            if any(math.hypot(key[0] - k[0], key[1] - k[1]) <= 0.15 for k in cl):
                cl.append(key)
                canon[key] = cl[0]
                placed = True
                break
        if not placed:
            clusters.append([key])
            canon[key] = key

    rail_pads = []
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.GetNetCode() in nets:
                pp = p.GetPosition()
                sz = p.GetSize()
                rail_pads.append((pp.x / MM, pp.y / MM,
                                  max(sz.x, sz.y) / 2 / MM))

    def nid(x, y):
        key = (round(x, 3), round(y, 3))
        key = canon.get(key, key)
        if key not in nodes:
            nodes[key] = len(nodes)
        return nodes[key]

    edges = []  # (a, b, R)
    segments = []  # (ax, ay, bx, by, R, w_m)
    for t in tracks:
        if t.GetNetCode() not in nets:
            continue
        if isinstance(t, pcbnew.PCB_VIA):
            p = t.GetPosition()
            # via joins layers at one (x, y): model as zero-R node merge by
            # using the same node id for both layers is implicit in 2D graph;
            # barrel resistance applies between the via point and itself ->
            # add small series R via a stub node.
            a = nid(p.x / MM, p.y / MM)
            b = nid(p.x / MM + 1e-4, p.y / MM)
            drill = t.GetDrill() / MM * 1e-3
            R = RHO * BOARD_T / (math.pi * drill * T_BARREL)
            edges.append((a, b, R))
        else:
            a_, b_ = t.GetStart(), t.GetEnd()
            ax, ay = a_.x / MM, a_.y / MM
            bx, by = b_.x / MM, b_.y / MM
            L = math.hypot(bx - ax, by - ay) * 1e-3
            w = t.GetWidth() / MM * 1e-3 * width_factor
            # split the segment at rail-net pad centres lying on it: pads
            # are where current enters/leaves, often mid-segment.
            dx, dy = bx - ax, by - ay
            L2 = dx * dx + dy * dy
            cuts = [(0.0, ax, ay), (1.0, bx, by)]
            if L2 > 0:
                for (px, py, _r) in rail_pads:
                    tt = ((px - ax) * dx + (py - ay) * dy) / L2
                    if 0.001 < tt < 0.999:
                        cx, cy = ax + tt * dx, ay + tt * dy
                        if math.hypot(px - cx, py - cy) <= 0.35:
                            cuts.append((tt, px, py))
            cuts.sort()
            for (t0, x0, y0), (t1, x1, y1) in zip(cuts, cuts[1:]):
                if t1 - t0 < 1e-6:
                    continue
                r_sub = RHO * L * (t1 - t0) / (w * T_CU)
                edges.append((nid(x0, y0), nid(x1, y1), r_sub))
                segments.append((x0, y0, x1, y1, r_sub, w, 0 if t.GetLayer() == pcbnew.F_Cu else 1))

    # junction ties: any graph node lying on a segment body (within its
    # half width + 0.05) joins that segment with proportional resistance.
    inv_nodes = {v: k for k, v in nodes.items()}
    for nid_v, (kx, ky) in inv_nodes.items():
        for (ax, ay, bx, by, r_seg, w_m, _lay) in segments:
            dx, dy = bx - ax, by - ay
            L2 = dx * dx + dy * dy
            if L2 == 0:
                continue
            tt = ((kx - ax) * dx + (ky - ay) * dy) / L2
            if tt <= 0.001 or tt >= 0.999:
                continue
            cx, cy = ax + tt * dx, ay + tt * dy
            if math.hypot(kx - cx, ky - cy) <= w_m * 500 + 0.05:
                edges.append((nid_v, nid(ax, ay), r_seg * (1 - tt) + 0.0005))
                edges.append((nid_v, nid(bx, by), r_seg * tt + 0.0005))

    # crossing ties: two same-layer segment bodies that touch/cross join
    # at their closest point with proportional resistance to all 4 ends.
    def seg_seg(a, b):
        (ax, ay, bx, by) = a
        (cx, cy, dx, dy) = b
        d1x, d1y = bx - ax, by - ay
        d2x, d2y = dx - cx, dy - cy
        denom = d1x * d2y - d1y * d2x
        if abs(denom) < 1e-12:
            return None
        t = ((cx - ax) * d2y - (cy - ay) * d2x) / denom
        u = ((cx - ax) * d1y - (cy - ay) * d1x) / denom
        if 0.001 < t < 0.999 and 0.001 < u < 0.999:
            return (t, u, ax + t * d1x, ay + t * d1y)
        return None
    for i in range(len(segments)):
        for j in range(i + 1, len(segments)):
            s1, s2 = segments[i], segments[j]
            if s1[6] != s2[6]:
                continue
            if max(s1[0], s1[2]) < min(s2[0], s2[2]) - 0.4 or \
               max(s2[0], s2[2]) < min(s1[0], s1[2]) - 0.4 or \
               max(s1[1], s1[3]) < min(s2[1], s2[3]) - 0.4 or \
               max(s2[1], s2[3]) < min(s1[1], s1[3]) - 0.4:
                continue
            hit = seg_seg(s1[:4], s2[:4])
            if hit:
                t, u, hx, hy = hit
                hn = nid(hx, hy)
                edges.append((hn, nid(s1[0], s1[1]), s1[4] * t + 0.0005))
                edges.append((hn, nid(s1[2], s1[3]), s1[4] * (1 - t) + 0.0005))
                edges.append((hn, nid(s2[0], s2[1]), s2[4] * u + 0.0005))
                edges.append((hn, nid(s2[2], s2[3]), s2[4] * (1 - u) + 0.0005))
    # pads join the graph at their centre (nearest node by position key)
    def pad_node(ref, num):
        for p in fps[ref].Pads():
            if p.GetNumber() == num:
                pos = p.GetPosition()
                return nid(pos.x / MM, pos.y / MM)
        raise KeyError(ref)

    # shunt edge between R_SHUNT pads (different nets, same component)
    edges.append((pad_node('R_SHUNT', '1'), pad_node('R_SHUNT', '2'), 0.010))
    src = pad_node('U_LDO', '5')
    loads = {}
    for g in 'ABC':
        for i in range(6):
            loads[pad_node(f'U_H{g}{i}', '1')] = 5e-3
        loads[pad_node(f'U_MUX{g}', '13')] = 0.1e-3
    loads[pad_node('R_DIV1', '1')] = 3.3 / 20000.0

    # model every rail-net pad as a junction: anything (track end or via)
    # touching the pad copper joins the pad-centre node at 0.5 mOhm.
    inv_nodes = {v: k for k, v in nodes.items()}
    for (px, py, pr) in rail_pads:
        centre = nid(px, py)
        for nid_v, (kx, ky) in inv_nodes.items():
            if nid_v != centre and math.hypot(kx - px, ky - py) <= pr + 0.06:
                edges.append((centre, nid_v, 0.0005))

    # tie each load/source pad-centre node to the nearest graph node that
    # carries an edge (tracks often land on a pad edge, not its centre);
    # 1 mOhm models the pad copper itself.
    inv = {v: k for k, v in nodes.items()}
    edge_nodes = set()
    for (a, b, R) in edges:
        edge_nodes.add(a)
        edge_nodes.add(b)
    for pn in list(loads) + [src]:
        if pn in edge_nodes:
            continue
        px, py = inv[pn]
        best, bd = None, 4.0
        for en in edge_nodes:
            ex, ey = inv[en]
            d = (ex - px) ** 2 + (ey - py) ** 2
            if d < bd:
                bd, best = d, en
        if best is not None:
            edges.append((pn, best, 0.001))
            edge_nodes.add(pn)

    # disc-overlap ties: two graph nodes whose copper discs overlap or
    # touch (via barrel r=0.30, track end r=its half width, pad r=its
    # radius) are one junction. All within one net, so a tie can only
    # merge copper that physically touches.
    node_r = {}
    for t in board.GetTracks():
        if t.GetNetCode() not in nets:
            continue
        if isinstance(t, pcbnew.PCB_VIA):
            p = t.GetPosition()
            node_r[nid(p.x / MM, p.y / MM)] = 0.30
        else:
            hw = t.GetWidth() / MM / 2
            for p in (t.GetStart(), t.GetEnd()):
                n_ = nid(p.x / MM, p.y / MM)
                node_r[n_] = max(node_r.get(n_, 0.0), hw)
    for (px, py, pr) in rail_pads:
        n_ = nid(px, py)
        node_r[n_] = max(node_r.get(n_, 0.0), pr)
    inv_nodes = {v: k for k, v in nodes.items()}
    ids = sorted(node_r)
    for ii in range(len(ids)):
        for jj in range(ii + 1, len(ids)):
            a, c = ids[ii], ids[jj]
            (ax, ay), (cx, cy) = inv_nodes[a], inv_nodes[c]
            if math.hypot(ax - cx, ay - cy) <= node_r[a] + node_r[c] + 0.01:
                edges.append((a, c, 0.0005))

    # restrict to the connected component containing the source; any load
    # outside it is a hard failure (rail does not reach that pad).
    adj = {}
    for (a, b, R) in edges:
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    seen = {src}
    stack = [src]
    while stack:
        n = stack.pop()
        for m in adj.get(n, []):
            if m not in seen:
                seen.add(m)
                stack.append(m)
    missing = [n for n in loads if n not in seen]
    if missing:
        inv = {v: k for k, v in nodes.items()}
        raise SystemExit(f'loads unreachable from LDO source: '
                         f'{[inv[n] for n in missing]}')
    edges = [(a, b, R) for (a, b, R) in edges if a in seen and b in seen]
    loads = {n: c for n, c in loads.items() if n in seen}

    idx = [n for n in seen if n != src]
    remap = {n: k for k, n in enumerate(idx)}
    G = np.zeros((len(idx), len(idx)))
    I = np.zeros(len(idx))
    for (a, b, R) in edges:
        g = 1.0 / R
        if a != src and b != src:
            G[remap[a], remap[a]] += g
            G[remap[b], remap[b]] += g
            G[remap[a], remap[b]] -= g
            G[remap[b], remap[a]] -= g
        elif a == src and b != src:
            G[remap[b], remap[b]] += g
            I[remap[b]] += g * 3.3
        elif b == src and a != src:
            G[remap[a], remap[a]] += g
            I[remap[a]] += g * 3.3
    for n, cur in loads.items():
        if n != src:
            I[remap[n]] -= cur
    V = np.linalg.solve(G, I)
    volts = {src: 3.3}
    for n, k in remap.items():
        volts[n] = V[k]
    drops = {}
    for g in 'ABC':
        for i in range(6):
            n = pad_node(f'U_H{g}{i}', '1')
            drops[f'U_H{g}{i}'] = (3.3 - volts[n]) * 1000.0
    return drops


board = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
out = {}
for label, wf in (('nominal', 1.0), ('width-20%', 0.8)):
    drops = solve(wf, board)
    worst = max(drops.items(), key=lambda kv: kv[1])
    out[label] = {'worst_sensor': worst[0], 'worst_droop_mV': round(worst[1], 2),
                  'mean_droop_mV': round(sum(drops.values()) / len(drops), 2)}
    print(f"{label}: worst {worst[0]} droop {worst[1]:.2f} mV, mean {out[label]['mean_droop_mV']} mV (budget 50 mV)")
json.dump(out, open(TREE / 'rail-droop-s2.json', 'w'), indent=1)
