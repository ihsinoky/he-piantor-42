"""R1 inventory: footprints/pads/tracks/vias/zones intersecting the notch
polygon (board frame) per variant."""
import sys, json
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/geometry/lib/python3.12/site-packages')
from shapely.geometry import Polygon, LineString, Point
import pcbnew as p
from pathlib import Path
RT = Path('/home/hatch/workspace/projects/he-piantor-boards/.issue263-runtime')
E = Path('/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation')
design = json.load(open(RT / 'r1-notch-design.json'))
wj = json.load(open(RT / 'r1-wings.json'))
MM = lambda v: p.ToMM(v)

for name in sorted(design):
    d = design[name]
    prof = d['profile']
    edge_x = d['edge_x']
    ext = -2.0 if 'right' in name else 2.0
    notch = Polygon(prof + [(edge_x + ext, d['y_lo']), (edge_x + ext, d['y_hi'])])
    b = p.LoadBoard(str(E / name / 'routed.kicad_pcb'))
    fps, pads, tracks, vias, zones = [], [], [], [], []
    for f in b.GetFootprints():
        bb = f.GetBoundingBox()
        fp_poly = Polygon([(MM(bb.GetLeft()), MM(bb.GetTop())), (MM(bb.GetRight()), MM(bb.GetTop())),
                           (MM(bb.GetRight()), MM(bb.GetBottom())), (MM(bb.GetLeft()), MM(bb.GetBottom()))])
        if fp_poly.intersects(notch):
            fps.append(f.GetReference())
        for pad in f.Pads():
            c = pad.GetCenter()
            if notch.contains(Point(MM(c.x), MM(c.y))):
                pads.append((f.GetReference(), pad.GetNumber(), pad.GetNetname()))
    for t in b.GetTracks():
        s, e = t.GetStart(), t.GetEnd()
        seg = LineString([(MM(s.x), MM(s.y)), (MM(e.x), MM(e.y))])
        if seg.intersects(notch):
            (vias if t.Type() == p.PCB_VIA_T else tracks).append(t.GetNetname())
    for z in b.Zones():
        bb = z.GetBoundingBox()
        zp = Polygon([(MM(bb.GetLeft()), MM(bb.GetTop())), (MM(bb.GetRight()), MM(bb.GetTop())),
                      (MM(bb.GetRight()), MM(bb.GetBottom())), (MM(bb.GetLeft()), MM(bb.GetBottom()))])
        if zp.intersects(notch):
            zones.append(z.GetNetname())
    from collections import Counter
    print(f"== {name}: footprints {sorted(set(fps))}; pads {pads}", flush=True)
    print(f"   tracks by net {dict(Counter(tracks))}; vias by net {dict(Counter(vias))}; zones {sorted(set(zones))}", flush=True)
print('done')
