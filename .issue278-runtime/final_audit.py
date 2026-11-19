#!/usr/bin/env python3
"""Issue #278 final audit: Family A2 = A1-fixed centreline (168.64 mm)
+ route channel cutters z 1.20..3.40 (the diagnostic showed the tray
top along the route is ~2.0, locally 3.0 at the pocket rim - the A1
cutters at z 1.22..1.62 were too shallow). Full fitted gate from the
STEP cache. Saves gate results BEFORE the (slow) extrema step."""
import sys, os, json, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import local_lib as LL
import numpy as np
from build123d import Box, Pos, Rot

RT = LL.RT

def log(*a): print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)

def main():
    bodies = LL.load_bodies()
    log(f"bodies loaded: {len(bodies)}")
    # Positive controls (the old plug-vs-tray-left '22.75' was a
    # fail-open intersect artifact on a disjoint Compound pair - see
    # decisive.py: in-process tray-left is a 7.4 mm3 fragment compound,
    # bbox-disjoint from every cable; gates never depended on it).
    b1 = LL.box_at(0, 0, 0, 4, 4, 2)
    b2 = LL.box_at(1, 1, 0.5, 4, 4, 2)
    st1 = round(LL.common_vol(b1, b2), 3)   # expect 3*3*1.5 = 13.5
    A0 = [(0,19.18,3.45),(0,22.5,3.0),(1.5,25.5,2.5),(4,28,2.2),
          (11,32,2.2),(16.5,38,2.2),(17,44,2.2),(14.5,49.5,2.2),(9,48,2.2),
          (6.5,41,2.2),(6.5,30,2.2),(7.5,22,2.2),(10.5,14,2.2),(10.5,4,2.2),
          (13,-4,2.2),(10.5,-13,2.2),(13,-22,2.2),(10.5,-31,2.2),
          (8,-39,2.2),(4,-44,2.25),(1,-46.6,2.6),(0,-48,3.0),(0,-49.02,3.45)]
    c0, _ = LL.cable_solid(A0)
    st2 = round(LL.common_vol(c0, bodies['tray-right']), 2)  # in-process: 321.58
    st = dict(synthetic=st1, A0_vs_tray_right_cache=st2)
    log(f"positive controls: {st}")

    pts = LL.catmull(LL.A1F)
    cutters = []
    for a, b in zip(pts[:-1], pts[1:]):
        d = np.array(b) - np.array(a); Ln = float(np.linalg.norm(d))
        if Ln < 1e-6: continue
        yaw = math.degrees(math.atan2(d[1], d[0]))
        mid = (np.array(a) + np.array(b)) / 2
        cutters.append(Pos(float(mid[0]), float(mid[1]), 2.30) * Rot(0, 0, yaw)
                       * Box(Ln + 1.2, 7.5, 2.20))
    chan = LL.fuse_all(cutters)
    log(f"channel cutter fused, gross volume {round(LL.vol(chan), 1)}")

    removed = {}
    for tn in ('tray-right', 'tray-left'):
        before = LL.vol(bodies[tn])
        bodies[tn] = bodies[tn].cut(chan)
        removed[tn] = round(before - LL.vol(bodies[tn]), 1)
    log(f"removed tray material: {removed}")

    cable, L = LL.cable_solid(LL.A1F)
    hits, eng = LL.gate(cable, bodies)
    log(f"A2: length={L} hits={hits} engagement={eng}")
    d = json.load(open(os.path.join(RT, 'audit278.json')))
    d['A2'] = dict(length_mm=L, hits=hits, engagement=eng,
                   channel_removed_mm3=removed,
                   channel_gross_mm3=round(LL.vol(chan), 1),
                   self_test_cache=st)
    json.dump(d, open(os.path.join(RT, 'audit278.json'), 'w'), indent=1)
    log("gate saved; extrema next")
    d['A2']['sheet_clearance'] = {
        s: round(LL.extrema(cable, bodies[f'FFC-sheet-{s}']), 3)
        for s in ('right', 'left')}
    json.dump(d, open(os.path.join(RT, 'audit278.json'), 'w'), indent=1)
    log(f"A2 sheet clearance: {d['A2']['sheet_clearance']}")
    log("DONE")

if __name__ == '__main__':
    main()
