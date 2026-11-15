import sys, json
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
from common import *
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.gp import gp_Pnt
idx, raw = cached(17)
solids = {}
for (name, k, s), r in zip(raw, idx):
    solids.setdefault(name, []).append(s)
def box(cx, cy, cz, h=0.3):
    return Shape.cast(BRepPrimAPI_MakeBox(gp_Pnt(cx-h, cy-h, cz-h), gp_Pnt(cx+h, cy+h, cz+h)).Shape())
PLANES = {1: 35.125, 7: 27.625, 14: 18.875}
ZS = [5.1, 6.6, 8.0, 9.5, 11.0, 12.8, 14.0, 15.1]
YS = [round(-34 + 1.0*k, 1) for k in range(67)]
out = {}
for pin, x0 in PLANES.items():
    # prefilter solids whose AABB meets the column
    cand = {}
    for n, ss in solids.items():
        if n.startswith(('Wire-', 'USB-')): continue
        for s in ss:
            bb = s.bounding_box()
            if bb.min.X-0.6 <= x0 <= bb.max.X+0.6 and bb.min.Y-0.6 <= 32 and bb.max.Y+0.6 >= -34 and bb.min.Z-0.6 <= 15.6 and bb.max.Z+0.6 >= 4.8:
                cand.setdefault(n, []).append(s)
    grid = {}
    for y in YS:
        row = {}
        for z in ZS:
            b = box(x0, y, z)
            hit = None
            for n, ss in cand.items():
                for s in ss:
                    bb = s.bounding_box()
                    if bb.min.X-0.35 <= x0 <= bb.max.X+0.35 and bb.min.Y-0.35 <= y <= bb.max.Y+0.35 and bb.min.Z-0.35 <= z <= bb.max.Z+0.35:
                        if volume(b, s) > 1e-4: hit = n; break
                if hit: break
            row[z] = hit
        grid[y] = row
    out[pin] = grid
    print(f'--- plane pin {pin} x0={x0}: Y rows where FULL column Z5.1..15.1 is clear:')
    for y in YS:
        if all(grid[y][z] is None for z in ZS):
            print('   clear Y =', y)
    print(f'--- blockers summary pin {pin}:')
    from collections import Counter
    c = Counter(v for row in grid.values() for v in row.values() if v)
    print('   ', dict(c))
json.dump({str(k): {str(y): {str(z): v for z, v in row.items()} for y, row in g.items()} for k, g in out.items()},
          open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round11/column-scan.json', 'w'), indent=0)
print('saved column-scan.json')
