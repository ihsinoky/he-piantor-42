"""Full-grid disk placement scan: R=9.2 disk clearance for centres
Cx 10..30 step 2, Cy -10..20 step 2, Z in 11 levels 5.2..19.0.
Dumps the whole grid to RT15/disk_grid.json for placement solving."""
import sys, json
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round15')
from common import *
from exact_oracle import OracleBody

BOX_LO = np.array([-44., -24., 2.]); BOX_HI = np.array([48., 46., 24.])
OBS = []
for pitch in (17, 16):
    idx, raw = cached(pitch)
    for n, k, s in raw:
        if n.startswith('Wire'): continue
        lo = np.array([s.bounding_box().min.X, s.bounding_box().min.Y, s.bounding_box().min.Z])
        hi = np.array([s.bounding_box().max.X, s.bounding_box().max.Y, s.bounding_box().max.Z])
        if np.any(hi < BOX_LO) or np.any(lo > BOX_HI): continue
        ob = OracleBody(n, s).restrict(BOX_LO - 3, BOX_HI + 3)
        if len(ob.faces): OBS.append((pitch, n, ob))
print('bodies:', len(OBS), flush=True)
LO = np.array([ob.lo for _, _, ob in OBS]); HI = np.array([ob.hi for _, _, ob in OBS])
angs = np.linspace(0, 2 * np.pi, 32, endpoint=False)
grid = {}
for Z in (5.0, 6.05, 7.1, 8.15, 9.2, 10.25, 11.3, 12.35, 13.4, 14.45, 15.5, 16.55, 17.6, 18.65):
    for cx in np.arange(10., 30.01, 2.0):
        for cy in np.arange(-10., 20.01, 2.0):
            worst = 9.0
            pts = np.column_stack([cx + 9.2 * np.cos(angs), cy + 9.2 * np.sin(angs), np.full(32, Z)])
            for p in pts:
                dlb = np.maximum(np.maximum(LO - p, p - HI), 0.0)
                d2 = np.sum(dlb * dlb, axis=1)
                for k in np.where(d2 < 4.0)[0]:
                    d, q = OBS[k][2].dist(p)
                    if d < worst: worst = float(d)
            grid[f'{cx:.0f},{cy:.0f},{Z}'] = round(worst, 3)
    good = {k: v for k, v in grid.items() if k.endswith(f',{Z}') and v >= 0.55}
    print('Z', Z, 'centres with clearance>=0.55:', len(good), flush=True)
    json.dump(grid, open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round15/disk_grid.json', 'w'), indent=0)
print('saved disk_grid.json', flush=True)
