#!/usr/bin/env python3
"""Issue #278 diagnostic v2 (cache-based): localize A1F cable x tray
intersection (bbox, pieces, z/y slices) + tray top profile probes."""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import local_lib as LL
from build123d import Box, Pos

RT = LL.RT

def log(*a): print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)

def main():
    trays = LL.load_bodies({'tray-right', 'tray-left'})
    log("trays loaded")
    cable, L = LL.cable_solid(LL.A1F)
    log(f"cable built, length {L}")
    out = {}
    for tn, tray in trays.items():
        inter = cable.intersect(tray)
        v = LL.vol(inter)
        rec = dict(volume=round(v, 3))
        if v > 0:
            pieces = list(inter) if not hasattr(inter, 'bounding_box') else [inter]
            inter = LL.fuse_all(pieces) if len(pieces) > 1 else pieces[0]
            bbs = [p.bounding_box() for p in pieces]
            rec['n_pieces'] = len(pieces)
            rec['bbox'] = [round(min(b.min.X for b in bbs), 2),
                           round(min(b.min.Y for b in bbs), 2),
                           round(min(b.min.Z for b in bbs), 2),
                           round(max(b.max.X for b in bbs), 2),
                           round(max(b.max.Y for b in bbs), 2),
                           round(max(b.max.Z for b in bbs), 2)]
            rec['piece_volumes'] = sorted([round(LL.vol(p), 2) for p in pieces],
                                          reverse=True)[:12]
            zs = {}
            for z0 in (0.0, 0.6, 1.0, 1.3, 1.6, 1.9, 2.2, 2.5, 2.8):
                clip = Pos(0, 0, z0 + 0.15) * Box(400, 400, 0.3)
                zs[str(z0)] = round(LL.vol(inter.intersect(clip)), 3)
            rec['z_slices_0.3'] = zs
            ys = {}
            for y0 in range(-50, 60, 10):
                clip = Pos(0, y0 + 5, 2) * Box(400, 10, 20)
                ys[str(y0)] = round(LL.vol(inter.intersect(clip)), 3)
            rec['y_slices_10'] = ys
        out[tn] = rec
        log(f"{tn}: {json.dumps(rec)}")
    # tray top probes: thin vertical column at route points; report the
    # tray material z-extent under each probe (via slice volumes)
    probes = [(10.5, 10), (10.5, -20), (17, 40), (6.5, 35), (20, -6),
              (2, -24), (8, -42), (0, -30), (14, 47)]
    pr = {}
    tray = trays['tray-right']
    for (px, py) in probes:
        col = Pos(px, py, 2) * Box(1.0, 1.0, 8)
        inter = col.intersect(tray)
        v = LL.vol(inter)
        if v > 0:
            pieces = list(inter) if not hasattr(inter, 'bounding_box') else [inter]
            bbs = [p.bounding_box() for p in pieces]
            pr[f"{px},{py}"] = dict(
                vol=round(v, 2),
                zmin=round(min(b.min.Z for b in bbs), 2),
                zmax=round(max(b.max.Z for b in bbs), 2),
                n=len(pieces))
        else:
            pr[f"{px},{py}"] = dict(vol=0.0)
    out['tray_top_probes'] = pr
    log(f"probes: {json.dumps(pr)}")
    json.dump(out, open(os.path.join(RT, 'diag_tray.json'), 'w'), indent=1)
    log("DONE")

if __name__ == '__main__':
    main()
