#!/usr/bin/env python3
"""Issue #278 continuation (run 1 was killed by a service restart during
the B body build; A0/D/C/sweeps are already in audit278.json).
Audits: B (mirrored Stage B hop, east) and A1-fixed (channel route,
centreline plan-fixed vs joint-screw posts, slack dress tuned to the
170 mm stock cable). Lengths are computed first (cheap) and the
A1 variant in [166,170] mm is chosen before any body build."""
import sys, os, json, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import route_audit as RA
from build123d import Box, Pos, Rot
import numpy as np
import audit_static as AS

RT = RA.RT
OUT = json.load(open(os.path.join(RT, 'audit278.json')))

def log(*a): print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)

def centre_len(ctrl):
    pts = AS.catmull(ctrl)
    return round(sum(float(np.linalg.norm(np.array(pts[i+1]) - np.array(pts[i])))
                     for i in range(len(pts) - 1)), 2)

def a1_variant(W):
    return [(0,19.18,3.45),(0,22.5,2.9),(1.5,25.5,2.2),(4,28,1.95),
            (11,32,1.9),(16.5,38,1.9),(17,44,1.9),(14.5,50,1.9),(9,48,1.9),
            (6.5,41,1.9),(6.5,30,1.9),(7.5,22,1.9),(10.5,14,1.9),(10.5,5,1.9),
            (20,-3,1.9),(20,-9,1.9),(10.5,-15,1.9),
            (W,-21,1.9),(W,-27,1.9),(10.5,-33,1.9),
            (8,-39,1.9),(5.5,-44.5,1.95),(1,-46.6,2.3),(0,-48,2.85),
            (0,-49.02,3.45)]

def main():
    cands = {}
    for W in (0, 2, -2):
        c = a1_variant(W)
        cands[W] = (centre_len(c), c)
        log(f"A1 variant W={W}: centreline {cands[W][0]} mm")
    pick = None
    for W in (0, 2, -2):
        if 166.0 <= cands[W][0] <= 170.0:
            pick = W; break
    if pick is None:
        pick = min(cands, key=lambda w: abs(cands[w][0] - 168.0))
    A1F = cands[pick][1]
    log(f"A1-fixed: W={pick}, length {cands[pick][0]} mm")
    OUT['A1_fixed_plan'] = dict(W=pick, length_mm=cands[pick][0],
                                lengths_all={str(w): cands[w][0] for w in cands})
    json.dump(OUT, open(os.path.join(RT, 'audit278.json'), 'w'), indent=1)

    # ---- Family B: mirrored Stage B hop route + channel E ----
    chanE = RA.box_at(10.0, -9.0, 1.10, 5.0, 56.0, 1.0)
    log("building bodies (B: + channel E)")
    bodiesB, _ = RA.build_bodies(extra_tray_cuts=(chanE,))
    c, L = RA.cable_solid(RA.B)
    hits, eng = RA.gate(c, bodiesB, 'B')
    OUT['B'] = dict(length_mm=L, hits=hits, engagement=eng)
    json.dump(OUT, open(os.path.join(RT, 'audit278.json'), 'w'), indent=1)

    # ---- Family A1-fixed: route channel cutters ----
    pts = AS.catmull(A1F)
    cutters = []
    for a, b in zip(pts[:-1], pts[1:]):
        d = np.array(b) - np.array(a); Ln = float(np.linalg.norm(d))
        if Ln < 1e-6: continue
        yaw = math.degrees(math.atan2(d[1], d[0]))
        mid = (np.array(a) + np.array(b)) / 2
        cutters.append(Pos(float(mid[0]), float(mid[1]), 1.42) * Rot(0, 0, yaw)
                       * Box(Ln + 1.2, 7.5, 0.40))
    chanA1 = RA.fuse_all(cutters)
    log("building bodies (A1-fixed: + route channel)")
    bodiesA, sheetsA = RA.build_bodies(extra_tray_cuts=(chanA1,))
    c, L = RA.cable_solid(A1F)
    hits, eng = RA.gate(c, bodiesA, 'A1-fixed')
    OUT['A1_fixed'] = dict(length_mm=L, hits=hits, engagement=eng,
                           channel_cut_volume_mm3=round(RA.vol(chanA1), 1))
    OUT['A1_fixed']['sheet_clearance'] = {
        s: round(RA.extrema(c, sheetsA[s]), 3) for s in ('left', 'right')}
    json.dump(OUT, open(os.path.join(RT, 'audit278.json'), 'w'), indent=1)
    log("DONE")

if __name__ == '__main__':
    main()
