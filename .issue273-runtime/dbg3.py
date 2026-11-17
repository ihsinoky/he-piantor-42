"""Dump the ordered Edge.Cuts chain (case frame) in the notch window
for the 17mm variants, from the saved Rev.6 boards."""
import sys
from pathlib import Path
from collections import defaultdict
import pcbnew as p
from shapely.geometry import Point
from shapely.affinity import rotate as shp_rotate, translate as shp_translate
MM = 1e6
W = Path("/home/hatch/workspace/projects/he-piantor-wingnotch")
sys.path.insert(0, "/home/hatch/workspace/projects/he-piantor-mainoutline/.issue270-runtime")
from notchain import wing_xf_factory
Q263 = W / "hardware/kicad/qualification/issue-263-implementation"
Q270W = W / "hardware/kicad/qualification/issue-270-wing-rev6"

for variant in ("17mm-left", "17mm-right"):
    pitch, side = variant.split("-")
    deg = 30.5 if side == "left" else -30.5
    env = (-27.0, -37.5) if side == "left" else (27.0, -37.5)
    b5 = p.LoadBoard(str(Q263 / f"wing-rev5-{variant}/main.kicad_pcb"))
    b6 = p.LoadBoard(str(Q270W / f"wing-rev6-{variant}/main.kicad_pcb"))
    fwd, inv, jw = wing_xf_factory(b5, side)
    def tc(pt):
        q = shp_translate(Point(pt), xoff=-jw[0], yoff=-jw[1])
        q = shp_rotate(q, deg, origin=(0, 0))
        q = shp_translate(q, xoff=env[0], yoff=env[1])
        return (round(q.x, 3), round(q.y, 3))
    els = []
    for d in b6.GetDrawings():
        if d.GetLayer() != p.Edge_Cuts:
            continue
        s = (d.GetStart().x / MM, d.GetStart().y / MM)
        e = (d.GetEnd().x / MM, d.GetEnd().y / MM)
        els.append((str(d.GetShape()), s, e))
    def key(pt):
        return (round(pt[0], 4), round(pt[1], 4))
    by_start = defaultdict(list)
    for i, el in enumerate(els):
        by_start[key(el[1])].append(i); by_start[key(el[2])].append(i)
    used = [False] * len(els); chain = []
    used[0] = True; chain.append(els[0]); curpt = els[0][2]
    for _ in range(len(els) - 1):
        nxt = next((i for i in by_start[key(curpt)] if not used[i]), None)
        if nxt is None: break
        used[nxt] = True; el = els[nxt]
        if key(el[1]) == key(curpt):
            chain.append(el); curpt = el[2]
        else:
            chain.append((el[0], el[2], el[1])); curpt = el[1]
    print(f"== {variant} chain window:")
    for shp, s, e in chain:
        sc, ec = tc(s), tc(e)
        if side == "left":
            inwin = (-42 < sc[0] < -8 and 24 < sc[1] < 62) or (-42 < ec[0] < -8 and 24 < ec[1] < 62)
        else:
            inwin = (8 < sc[0] < 42 and 24 < sc[1] < 62) or (8 < ec[0] < 42 and 24 < ec[1] < 62)
        if inwin:
            import math
            ln = math.dist(sc, ec)
            print(f"  {shp} {sc} -> {ec}  len {ln:.3f}")
