import sys
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round10')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round9')
from common import *
from concepts import concept_C
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.gp import gp_Pnt
idx, raw = cached(17)
solids = {}
for (name, k, s), r in zip(raw, idx):
    solids.setdefault(name, []).append(s)
fixed = {n: v for n, v in solids.items() if not n.startswith(('Wire-', 'USB-'))}
def box(cx, cy, cz, h=0.4):
    return Shape.cast(BRepPrimAPI_MakeBox(gp_Pnt(cx-h, cy-h, cz-h), gp_Pnt(cx+h, cy+h, cz+h)).Shape())
for i in (0, 6, 13):
    st = concept_C(i); pts, segs = st.samples()
    inside = {}
    for p in pts[::3]:
        b = box(p[0], p[1], p[2])
        for n, ss in fixed.items():
            for s in ss:
                bb = s.bounding_box()
                if (bb.min.X-0.5 <= p[0] <= bb.max.X+0.5 and bb.min.Y-0.5 <= p[1] <= bb.max.Y+0.5 and bb.min.Z-0.5 <= p[2] <= bb.max.Z+0.5):
                    if volume(b, s) > 1e-4:
                        inside.setdefault(n, []).append((round(p[0],1), round(p[1],1), round(p[2],1)))
    print(f'strand {i+1}: centreline points inside fixed solids:')
    for n, ps in inside.items():
        print('  ', n, 'count', len(ps), 'sample', ps[:4])
    if not inside: print('   CLEAR')
