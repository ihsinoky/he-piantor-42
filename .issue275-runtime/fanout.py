"""Analyse J2/J3 fanout: tracks/vias touching each pad, far endpoints."""
import json, math
from pathlib import Path
import pcbnew as p

MM = 1e6
SRC = Path("/home/hatch/workspace/projects/he-piantor-mainsym/hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb")
b = p.LoadBoard(str(SRC))

tracks = list(b.GetTracks())
def ep(t):
    s, e = t.GetStart(), t.GetEnd()
    return (s.x / MM, s.y / MM), (e.x / MM, e.y / MM)

for ref in ("J2", "J3"):
    fp = b.FindFootprintByReference(ref)
    print(f"== {ref} ==")
    for a in sorted(fp.Pads(), key=lambda q: q.GetNumber()):
        pp = a.GetPosition()
        px, py = pp.x / MM, pp.y / MM
        hits = []
        for t in tracks:
            (x1, y1), (x2, y2) = ep(t)
            for (hx, hy, tag) in ((x1, y1, "s"), (x2, y2, "e")):
                if math.hypot(hx - px, hy - py) < 0.75:
                    other = (x2, y2) if tag == "s" else (x1, y1)
                    hits.append({"kind": "via" if isinstance(t, p.PCB_VIA) else "trk",
                                 "uuid": t.m_Uuid.AsString()[:8], "layer": t.GetLayer(),
                                 "at": [round(hx, 4), round(hy, 4)], "far": [round(other[0], 4), round(other[1], 4)],
                                 "w": round(t.GetWidth(p.F_Cu) / MM, 3) if isinstance(t, p.PCB_VIA) else round(t.GetWidth() / MM, 3)})
        print(f" pad {a.GetNumber():>3} net {a.GetNetname():<10} at ({px:.4f},{py:.4f}) hits={len(hits)}")
        for h in hits:
            print("    ", h)
