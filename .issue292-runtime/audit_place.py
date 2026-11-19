"""Placement audit (pure-python geometry): pads vs outline polygon,
courtyard bbox vs trackpad circle / outline, courtyard overlaps, pocket data."""
import pcbnew as p, sys, json, math
from pathlib import Path
E = Path('.').resolve(); W = E.parent
TREE = W/'hardware/kicad/qualification/issue-292-wmain'
b = p.LoadBoard(str(TREE/'wmain.kicad_pcb'))
LOOP = [(64.1073, 134.4359), (66.1073, 137.9), (133.8927, 137.9), (135.8927, 134.4359),
        (128.9362, 122.3869), (132.9488, 115.4381), (119.8213, 103.1964),
        (117.8562, 103.1958), (102.0, 75.7321), (98.0, 75.7321), (82.1438, 103.1958),
        (80.1787, 103.1964), (67.0512, 115.4381), (71.0638, 122.3869)]

def in_poly(x, y):
    inside = False
    n = len(LOOP)
    for i in range(n):
        x1, y1 = LOOP[i]; x2, y2 = LOOP[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xin = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xin:
                inside = not inside
    return inside

def seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))

def outline_dist(x, y):
    return min(seg_dist(x, y, *LOOP[i], *LOOP[(i + 1) % len(LOOP)]) for i in range(len(LOOP)))

def box_circle_hit(bx0, by0, bx1, by1, cx=100.0, cy=118.0, r=20.0):
    nx = max(bx0, min(cx, bx1)); ny = max(by0, min(cy, by1))
    return math.hypot(cx - nx, cy - ny) < r

res = {'pads_outside_outline': [], 'courtyard_in_trackpad_circle': [],
       'courtyard_outside_outline': [], 'fp_overlaps': []}
courts = {}
for f in b.GetFootprints():
    ref = str(f.GetReference())
    pads = list(f.Pads())
    xs = [p.ToMM(a.GetPosition().x) for a in pads]; ys = [p.ToMM(a.GetPosition().y) for a in pads]
    bx = (min(xs) - 0.45, min(ys) - 0.45, max(xs) + 0.45, max(ys) + 0.45)
    courts[ref] = bx
    hit = False
    for a_ in pads:
        px, py = p.ToMM(a_.GetPosition().x), p.ToMM(a_.GetPosition().y)
        sx, sy = p.ToMM(a_.GetSize().x) / 2 + 0.45, p.ToMM(a_.GetSize().y) / 2 + 0.45
        if box_circle_hit(px - sx, py - sy, px + sx, py + sy):
            hit = True
    if hit:
        res['courtyard_in_trackpad_circle'].append(ref)
    corners = [(bx[0], bx[1]), (bx[2], bx[1]), (bx[2], bx[3]), (bx[0], bx[3])]
    if not all(in_poly(x, y) for (x, y) in corners):
        res['courtyard_outside_outline'].append(ref)
    for pad in f.Pads():
        px, py = p.ToMM(pad.GetPosition().x), p.ToMM(pad.GetPosition().y)
        if not in_poly(px, py):
            res['pads_outside_outline'].append(f"{ref}.{pad.GetNumber()} @({px:.2f},{py:.2f})")
refs = sorted(courts)
for i, r1 in enumerate(refs):
    for r2 in refs[i + 1:]:
        a, c = courts[r1], courts[r2]
        ox = max(0.0, min(a[2], c[2]) - max(a[0], c[0]))
        oy = max(0.0, min(a[3], c[3]) - max(a[1], c[1]))
        if ox * oy > 0.02:
            res['fp_overlaps'].append(f"{r1} x {r2}: {ox * oy:.2f} mm2")
u1 = [f for f in b.GetFootprints() if str(f.GetReference()) == 'U1'][0]
bb = u1.GetBoundingBox()
mb = [round(p.ToMM(bb.GetLeft()), 2), round(p.ToMM(bb.GetTop()), 2),
      round(p.ToMM(bb.GetRight()), 2), round(p.ToMM(bb.GetBottom()), 2)]
res['module_bbox'] = mb
nx = max(mb[0], min(100.0, mb[2])); ny = max(mb[1], min(118.0, mb[3]))
res['module_to_circle_clearance_mm'] = round(math.hypot(100 - nx, 118 - ny) - 20.0, 3)
res['module_west_outline_clearance_mm'] = round(min(outline_dist(mb[0], y) for y in (mb[1], (mb[1] + mb[3]) / 2, mb[3])), 3)
print(json.dumps(res, indent=1))
Path('audit-place.json').write_text(json.dumps(res, indent=1))
