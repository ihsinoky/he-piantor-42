import sys
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
from common import *
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.gp import gp_Pnt
idx, raw = cached(17)
solids = {}
for (name, k, s), r in zip(raw, idx):
    solids.setdefault(name, []).append(s)
def box(x0,y0,z0,x1,y1,z1):
    return Shape.cast(BRepPrimAPI_MakeBox(gp_Pnt(x0,y0,z0), gp_Pnt(x1,y1,z1)).Shape())
# crown band: all 14 planes x0 in [18.875,35.125] (+-0.5), crown leg Y[-2,10] Z[14.6,15.6]; up-arc region Y[5,15] Z[5.1,15.1] probed as Y[5,15] Z[12,15.6] upper part + full column test
probes = {
 'crown-leg band': box(18.3,-2.0,14.55, 35.7,10.0,15.65),
 'up-arc top band': box(18.3,5.0,13.0, 35.7,15.0,15.65),
 'descent band': box(18.3,-12.4,6.0, 35.7,-1.9,15.65),
 'exit band': box(18.3,-30.0,6.05, 35.7,-12.3,7.15),
}
names = [n for n in solids if not n.startswith(('Wire-','USB-'))]
for pn, pb in probes.items():
    hits = []
    for n in names:
        for s in solids[n]:
            v = volume(pb, s)
            if v > 1e-6: hits.append((n, round(v,3)))
    print(pn, '->', hits if hits else 'CLEAR')
