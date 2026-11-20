import sys, json
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
import fitlibF as FF
import repair18_lib as R
import fitlib18 as F
from build123d import Box, Pos, Cylinder
bodies = FF.bodies_at(17, -2.65)
bd = dict(bodies)

def top_z(names, x, y, zlo=-3.0, zhi=23.0):
    p = Pos(x, y, (zlo+zhi)/2) * Box(1.2, 1.2, zhi-zlo)
    best = None
    for n in names:
        s = bd[n]
        bb = s.bounding_box()
        if bb.min.X-1 > x or bb.max.X+1 < x or bb.min.Y-1 > y or bb.max.Y+1 < y: continue
        c = s & p
        if c is not None and c.volume > 1e-6:
            t = c.bounding_box().max.Z
            if best is None or t > best: best = t
    return best

print('== deck surface (max of tray/shell/plate) south-centre strip ==')
for y in (82, 78, 74, 70, 66, 62):
    cells = []
    for x in range(-36, 37, 6):
        t = top_z(('tray-left','tray-right','shell-central','plate-left','plate-right'), x, y)
        cells.append('  .  ' if t is None else f'{t:5.1f}')
    print(f'Y={y:3d}: ' + ' '.join(cells))
print('X: -36..36 step 6')

def disc_audit(label, cx, cy, r, zlo, zhi, skip=()):
    cyl = Pos(cx, cy, (zlo+zhi)/2) * Cylinder(radius=r, height=zhi-zlo)
    bb = cyl.bounding_box()
    hits = []
    for n, s in bodies:
        if n in skip: continue
        b2 = s.bounding_box()
        if (bb.max.X < b2.min.X-0.5 or bb.min.X > b2.max.X+0.5 or
            bb.max.Y < b2.min.Y-0.5 or bb.min.Y > b2.max.Y+0.5 or
            bb.max.Z < b2.min.Z-0.05 or bb.min.Z > b2.max.Z+0.05): continue
        v = R.vol_pair(cyl, s, F.bounds(cyl), F.bounds(s), repair=True)
        if v > F.HIT:
            hits.append((n, round(float(v), 3)))
    print(f'== {label}: centre ({cx},{cy}) r={r} Z {zlo}..{zhi} -> {hits}')

# (a) bay over Main: module underside resting over tallest comp (J4 top 8.00)+0.30, body 5.15+0.25 adh
disc_audit('A bay D40', 0, 32, 20.0, 8.30, 13.70)
# (b) thumb left: surface flush with plate 10.90, body below surface
disc_audit('B thumb D40', -55, 52, 20.0, 5.50, 10.90)
# (c) south-centre shelf: D23 sitting on shelf deck, body above deck ~13.0 assumed start
disc_audit('C south D23 @deck13', 0, 74, 11.5, 12.99, 18.39)
disc_audit('C south D40 @deck13', 0, 74, 20.0, 12.99, 18.39)
