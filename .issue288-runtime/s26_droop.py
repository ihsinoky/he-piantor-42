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

    def nid(x, y):
        key = (round(x, 3), round(y, 3))
        if key not in nodes:
            nodes[key] = len(nodes)
        return nodes[key]

    edges = []  # (a, b, R)
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
            L = math.hypot(b_.x - a_.x, b_.y - a_.y) / MM * 1e-3
            w = t.GetWidth() / MM * 1e-3 * width_factor
            if L > 0:
                edges.append((nid(a_.x / MM, a_.y / MM), nid(b_.x / MM, b_.y / MM),
                              RHO * L / (w * T_CU)))
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

    idx = [n for n in range(len(nodes)) if n != src]
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
