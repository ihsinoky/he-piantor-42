#!/usr/bin/env python3
"""Extract the ISP1807 land pattern from the maker's TB top-copper gerber.
Modal-coordinate state machine; apertures D27 (0.4x0.4) / D28 (0.8x0.8)."""
import re, json

path = 'tb-gerber/ISP1807-LR-TB_RevB_V01/ISP1807-LR_TestBoard_revB.GTL'
txt = open(path).read()
ap_size = {}
for m in re.finditer(r'%ADD(\d+)R,([\d.]+)X([\d.]+)\*%', txt):
    ap_size[m.group(1)] = (float(m.group(2)), float(m.group(3)))
targets = {k: v for k, v in ap_size.items() if v in [(0.4, 0.4), (0.8, 0.8)]}
print('target apertures:', targets)

x = y = None
cur = None
flashes = []
for line in txt.splitlines():
    line = line.strip().rstrip('*')
    if not line or line.startswith('G04') or line.startswith('%'):
        continue
    m = re.fullmatch(r'D(\d+)', line)
    if m and int(m.group(1)) >= 10:
        cur = m.group(1)
        continue
    m = re.fullmatch(r'(?:X(-?\d+))?(?:Y(-?\d+))?(?:D0([123]))?', line)
    if m and (m.group(1) or m.group(2) or m.group(3)):
        if m.group(1) is not None: x = int(m.group(1))/1000
        if m.group(2) is not None: y = int(m.group(2))/1000
        if m.group(3) == '3' and cur in targets and x is not None and y is not None:
            flashes.append((x, y, targets[cur][0]))
print('candidate flashes:', len(flashes))
best = None
for fx, fy, fs in flashes:
    n = [(px, py, ps) for px, py, ps in flashes if abs(px-fx) <= 4.6 and abs(py-fy) <= 4.6]
    if best is None or len(n) > len(best):
        best = n
print('largest cluster:', len(best))
xs = [p[0] for p in best]; ys = [p[1] for p in best]
cx, cy = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2
rel = sorted([(round(px-cx, 4), round(py-cy, 4), s) for px, py, s in best])
json.dump(rel, open('tb-pads.json', 'w'), indent=0)
print('cluster bbox x', min(xs), max(xs), ' y', min(ys), max(ys))
print('sizes:', {s: sum(1 for p in best if p[2] == s) for s in (0.4, 0.8)})
