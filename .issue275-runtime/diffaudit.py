"""Audit Rev.10 (KRT output) vs Rev.9: where did copper change?"""
import math
from pathlib import Path
import pcbnew as p

MM = 1e6
A = Path("/home/hatch/workspace/projects/he-piantor-mainsym/hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb")
B = Path("/home/hatch/workspace/projects/he-piantor-mainsym/hardware/kicad/qualification/issue-275-main-rev10/main-rev10/main.kicad_pcb")
ba, bb = p.LoadBoard(str(A)), p.LoadBoard(str(B))
J2C = (76.048074, 112.073215)

def items(b):
    d = {}
    for t in b.GetTracks():
        s, e = t.GetStart(), t.GetEnd()
        d[t.m_Uuid.AsString()] = ("via" if isinstance(t, p.PCB_VIA) else "trk", t.GetNetname(), t.GetLayer(),
                                  (s.x / MM, s.y / MM), (e.x / MM, e.y / MM))
    return d

ia, ib = items(ba), items(bb)
removed = {k: v for k, v in ia.items() if k not in ib}
added = {k: v for k, v in ib.items() if k not in ia}
changed = {k for k in ia if k in ib and ia[k] != ib[k]}
print("tracks total:", len(ia), "->", len(ib), "| removed:", len(removed), "added:", len(added), "changed-geom:", len(changed))

def zone(v):
    (x1, y1), (x2, y2) = v[3], v[4]
    d = min(math.hypot(x1 - J2C[0], y1 - J2C[1]), math.hypot(x2 - J2C[0], y2 - J2C[1]))
    return d

for name, coll in (("REMOVED", removed), ("ADDED", added)):
    far = {k: v for k, v in coll.items() if zone(v) > 10}
    print(name, "total", len(coll), "| farther than 10mm from J2:", len(far))
    from collections import Counter
    print("   by net:", Counter(v[1] for v in coll.values()))
    print("   by layer:", Counter(v[2] for v in coll.values()))
    for k, v in list(far.items())[:12]:
        print("   FAR", v)
for k in list(changed)[:10]:
    print("CHANGED", ia[k], "->", ib[k])

# footprint census check: J3 identical?
for ref in ("J3",):
    fa = ba.FindFootprintByReference(ref)
    fb = bb.FindFootprintByReference(ref)
    pa, pb = fa.GetPosition(), fb.GetPosition()
    print(ref, "pos same:", (pa.x, pa.y) == (pb.x, pb.y), "rot same:", fa.GetOrientationDegrees() == fb.GetOrientationDegrees())
    same = all((x.GetPosition().x, x.GetPosition().y) == (y.GetPosition().x, y.GetPosition().y)
               for x, y in zip(sorted(fa.Pads(), key=lambda q: q.GetNumber()), sorted(fb.Pads(), key=lambda q: q.GetNumber())))
    print(ref, "pads same:", same)
