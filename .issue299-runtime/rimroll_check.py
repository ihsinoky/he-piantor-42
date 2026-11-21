"""Rim-roll re-verification for the trimmed Wing outlines (Issue #299).

Replicates the Z-check sweep exactly (zcheck8.py pose()): east cell,
slide 2.0 mm, tip 0..35 deg about the rim pivot (pz = 0.15 + CZ),
envelope = fuse(pose(2,0), pose(2,35)). Board solids are extruded
from the KiCad outlines at case Z 4.70..5.90 (zcheck frame +2.65).
Left variants are mirrored to the right side (the sweep is symmetric
by construction of the mirrored notch). Control: the untrimmed 17R
outline must reproduce the Z-check clip (~10.2-10.4 mm3).
"""
import build123d as bd
import json

CZ = 2.65

def pose(slide=0.0, tip=0.0, pivot="rim"):
    yN = -59.62 + slide; yS = -9.12 + slide
    zc = 7.40 + CZ
    c = bd.Solid.make_cylinder(7.25, 50.5).moved(bd.Location((0, 0, 0), (90, 0, 0)))
    bb = c.bounding_box()
    cx = (bb.min.X + bb.max.X) / 2; cy = (bb.min.Y + bb.max.Y) / 2; cz = (bb.min.Z + bb.max.Z) / 2
    c = c.moved(bd.Location((15 - cx, (yN + yS) / 2 - cy, zc - cz)))
    if tip:
        pz = (0.15 + CZ) if pivot == "rim" else zc
        c = c.moved(bd.Location((0, -yS, -pz)))
        c = c.moved(bd.Location((0, 0, 0), (-tip, 0, 0)))
        c = c.moved(bd.Location((0, yS, pz)))
    return c

def board_solid(pts, mirror=False, delta=9.5):
    vs = []
    for (x, y) in pts:
        if mirror:
            x = -x
        vs.append((x + delta, y))
    if vs[0] == vs[-1]:
        vs = vs[:-1]
    face = bd.Polygon(*vs)
    return bd.extrude(face, amount=1.2).moved(bd.Location((0, 0, 7.35)))

def vol(r):
    if r is None:
        return 0.0
    return sum(s.volume for s in r.solids() if s.volume > 0.001)

polys = json.load(open("rimroll-polys.json"))
env = pose(2.0, 0).fuse(pose(2.0, 35, "rim"))
for name in ("17R-base", "16R-base", "17R-trim", "17L-trim", "16R-trim", "16L-trim"):
    mirror = name.startswith(("17L", "16L"))
    s = board_solid(polys[name], mirror=mirror)
    try:
        inter = env.intersect(s)
    except Exception:
        inter = None
    print(f"{name}: rim-roll envelope vs board = {vol(inter):.3f} mm3")
