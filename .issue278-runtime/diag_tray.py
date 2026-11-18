#!/usr/bin/env python3
"""Issue #278 diagnostic: localize the A1-fixed cable x tray-right
intersection (bbox + volume slices by z and by y)."""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import route_audit as RA
from build123d import Box, Pos

RT = RA.RT

def log(*a): print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)

A1F = [(0,19.18,3.45),(0,22.5,2.9),(1.5,25.5,2.2),(4,28,1.95),
       (11,32,1.9),(16.5,38,1.9),(17,44,1.9),(14.5,50,1.9),(9,48,1.9),
       (6.5,41,1.9),(6.5,30,1.9),(7.5,22,1.9),(10.5,14,1.9),(10.5,5,1.9),
       (20,-3,1.9),(20,-9,1.9),(10.5,-15,1.9),
       (2,-21,1.9),(2,-27,1.9),(10.5,-33,1.9),
       (8,-39,1.9),(5.5,-44.5,1.95),(1,-46.6,2.3),(0,-48,2.85),
       (0,-49.02,3.45)]

def main():
    log("building bodies (pocket A only)")
    bodies, _ = RA.build_bodies()
    cable, L = RA.cable_solid(A1F)
    log(f"cable length {L}")
    out = {}
    for tn in ('tray-right', 'tray-left'):
        inter = cable.intersect(bodies[tn])
        v = RA.vol(inter) if inter is not None else 0.0
        rec = dict(volume=round(v, 3))
        if v > 0:
            pieces = list(inter) if not hasattr(inter, 'bounding_box') else [inter]
            bbs = [p.bounding_box() for p in pieces]
            rec['bbox'] = [round(min(b.min.X for b in bbs), 2),
                           round(min(b.min.Y for b in bbs), 2),
                           round(min(b.min.Z for b in bbs), 2),
                           round(max(b.max.X for b in bbs), 2),
                           round(max(b.max.Y for b in bbs), 2),
                           round(max(b.max.Z for b in bbs), 2)]
            rec['n_pieces'] = len(pieces)
            zs = {}
            for z0 in (0.0, 0.6, 1.0, 1.3, 1.6, 1.9, 2.2, 2.5, 2.8):
                clip = Pos(0, 0, z0 + 0.15) * Box(400, 400, 0.3)
                zs[str(z0)] = round(RA.vol(inter.intersect(clip)), 3)
            rec['z_slices_0.3'] = zs
            ys = {}
            for y0 in range(-50, 60, 10):
                clip = Pos(0, y0 + 5, 2) * Box(400, 10, 20)
                ys[str(y0)] = round(RA.vol(inter.intersect(clip)), 3)
            rec['y_slices_10'] = ys
        out[tn] = rec
        log(f"{tn}: {json.dumps(rec)}")
    json.dump(out, open(os.path.join(RT, 'diag_tray.json'), 'w'), indent=1)
    log("DONE")

if __name__ == '__main__':
    main()
