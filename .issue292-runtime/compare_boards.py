"""Compare tree board vs swapped working copy: everything OUTSIDE the
module field must be identical (footprints, tracks, vias, zones).
Module field = 26mm box around U1 centre (75.1, 124.85)."""
import pcbnew as p, json
from pathlib import Path
E = Path('.').resolve()
TREE = E.parent/'hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb'
def load(f): return p.LoadBoard(str(f))
tree, work = load(TREE), load(E/'wmain-v28-fp.kicad_pcb')
CX, CY, HB = 75.1, 124.85, 13.0
def in_field(x, y): return abs(x-CX) < HB and abs(y-CY) < HB
def fp_sig(b):
    out = {}
    for f in b.GetFootprints():
        pos = f.GetPosition()
        out[str(f.GetReference())] = (f.GetFPID().GetLibItemName(),
            round(pos.x/1e6, 4), round(pos.y/1e6, 4), round(f.GetOrientationDegrees(), 3),
            len(list(f.Pads())))
    return out
ft, fw = fp_sig(tree), fp_sig(work)
diffs = {k: (ft.get(k), fw.get(k)) for k in set(ft) | set(fw) if ft.get(k) != fw.get(k)}
print('footprint diffs (all):')
for k, v in diffs.items(): print(' ', k, v)
def track_sig(b, outside=True):
    s = []
    for t in b.GetTracks():
        a, e = t.GetStart(), t.GetEnd()
        ax, ay, ex, ey = a.x/1e6, a.y/1e6, e.x/1e6, e.y/1e6
        inside = in_field(ax, ay) and in_field(ex, ey)
        if outside and inside: continue
        s.append((t.GetNetname(), t.GetLayer(), round(ax,3), round(ay,3),
                  round(ex,3), round(ey,3), round(t.GetWidth()/1e6, 3),
                  type(t).__name__))
    return sorted(s)
st, sw = track_sig(tree), track_sig(work)
print('tracks outside field: tree', len(st), 'work', len(sw), 'identical:', st == sw)
if st != sw:
    from collections import Counter
    ct, cw = Counter(st), Counter(sw)
    print(' only-tree:', list((ct-cw).items())[:6])
    print(' only-work:', list((cw-ct).items())[:6])
def zone_sig(b):
    return sorted((z.GetZoneName(), z.GetNetname(), z.GetLayer()) for z in b.Zones())
print('zones identical:', zone_sig(tree) == zone_sig(work))
# outline segments
def edge_sig(b):
    s = []
    for d in b.GetDrawings():
        if d.GetLayer() == p.Edge_Cuts:
            s.append((str(d.GetShape()), round(d.GetStart().x/1e6,3), round(d.GetStart().y/1e6,3),
                      round(d.GetEnd().x/1e6,3), round(d.GetEnd().y/1e6,3)))
    return sorted(s)
print('edge cuts: tree', len(edge_sig(tree)), 'work', len(edge_sig(work)),
      'identical:', edge_sig(tree) == edge_sig(work))
