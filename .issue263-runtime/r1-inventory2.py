"""R1 inventory 2: tracks/vias/pads within 0.6 mm of the notch polygon;
identify the unnamed zone intersecting it."""
import sys, json
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/geometry/lib/python3.12/site-packages')
from shapely.geometry import Polygon, LineString, Point
import pcbnew as p
from pathlib import Path
from collections import Counter
RT = Path('/home/hatch/workspace/projects/he-piantor-boards/.issue263-runtime')
E = Path('/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation')
design = json.load(open(RT / 'r1-notch-design.json'))
MM = lambda v: p.ToMM(v)

for name in sorted(design):
    d = design[name]
    edge_x = d['edge_x']
    ext = -2.0 if 'right' in name else 2.0
    notch = Polygon(d['profile'] + [(edge_x + ext, d['y_lo']), (edge_x + ext, d['y_hi'])])
    b = p.LoadBoard(str(E / name / 'routed.kicad_pcb'))
    near = []
    for t in b.GetTracks():
        s, e = t.GetStart(), t.GetEnd()
        seg = LineString([(MM(s.x), MM(s.y)), (MM(e.x), MM(e.y))])
        dist = seg.distance(notch)
        if dist < 0.6:
            near.append((t.GetNetname(), 'via' if t.Type() == p.PCB_VIA_T else 'trk', round(dist, 3)))
    zinfo = []
    for z in b.Zones():
        bb = z.GetBoundingBox()
        zp = Polygon([(MM(bb.GetLeft()), MM(bb.GetTop())), (MM(bb.GetRight()), MM(bb.GetTop())),
                      (MM(bb.GetRight()), MM(bb.GetBottom())), (MM(bb.GetLeft()), MM(bb.GetBottom()))])
        if zp.intersects(notch):
            zinfo.append((z.GetNetname(), z.GetZoneName(), z.GetIsRuleArea(), z.GetLayerSet().FmtHex() if hasattr(z.GetLayerSet(), 'FmtHex') else '?'))
    print(f"== {name}: near-copper {Counter([n[0] for n in near])}", flush=True)
    for n in near: print('   ', n, flush=True)
    print(f"   zones: {zinfo}", flush=True)
print('done')
