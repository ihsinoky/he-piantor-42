import sys
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
import fitlibF as FF
import repair18_lib as R
import fitlib18 as F
from build123d import Box, Pos, Cylinder
bodies = FF.bodies_at(17, -2.65)
bd = dict(bodies)
for n in ('Main-study-C26','Main-study-C27','Main-study-C28','Main-study-J4','Main-study-U1'):
    bb = bd[n].bounding_box()
    print(f'{n:18s} X {bb.min.X:7.2f}..{bb.max.X:7.2f}  Y {bb.min.Y:7.2f}..{bb.max.Y:7.2f}  Z {bb.min.Z:5.2f}..{bb.max.Z:5.2f}')
# tray outline max Y near centre
for n in ('tray-left','tray-right'):
    s = bd[n]
    probe = Pos(0, 40, 10) * Box(24, 90, 26)
    c = s & probe
    bb = c.bounding_box()
    print(f'{n}: within |X|<=12, max Y = {bb.max.Y:.2f}, top Z at south rim region = {bb.max.Z:.2f}')
def disc_audit(label, cx, cy, r, zlo, zhi):
    cyl = Pos(cx, cy, (zlo+zhi)/2) * Cylinder(radius=r, height=zhi-zlo)
    bb = cyl.bounding_box()
    hits = []
    for n, s in bodies:
        if 'DRAWING-BOUND' in n: continue  # excluded per #261 audit convention
        b2 = s.bounding_box()
        if (bb.max.X < b2.min.X-0.5 or bb.min.X > b2.max.X+0.5 or
            bb.max.Y < b2.min.Y-0.5 or bb.min.Y > b2.max.Y+0.5 or
            bb.max.Z < b2.min.Z-0.05 or bb.min.Z > b2.max.Z+0.05): continue
        v = R.vol_pair(cyl, s, F.bounds(cyl), F.bounds(s), repair=True)
        if v > F.HIT:
            hits.append((n, round(float(v), 3)))
    print(f'== {label}: centre ({cx},{cy}) r={r} Z {zlo}..{zhi} -> {hits}')
disc_audit('A2 bay-north D40', 0, 48, 20.0, 7.30, 12.70)
disc_audit('A2 bay-north D35', 0, 48, 17.5, 7.30, 12.70)
# corner sections for the D40 at (0,48): shell bottom/top at centre + 4 quadrant pts + south rim
shell = bd['shell-central']
def probe(solid, x, y):
    p = Pos(x, y, 11) * Box(1.2, 1.2, 30)
    c = solid & p
    if c is None or c.volume < 1e-6: return None
    bb = c.bounding_box()
    return (round(bb.min.Z,2), round(bb.max.Z,2))
for (x, y) in [(0,48),(14,62),(-14,62),(14,34),(-14,34),(0,28),(0,68)]:
    print(f'shell at ({x},{y}): {probe(shell, x, y)}')
