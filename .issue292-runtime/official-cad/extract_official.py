#!/usr/bin/env python3
"""Extract official ISP1807-LR pad table from Insight SiP Eagle library.
Output: official-pads.json {pin: [x, y, dx, dy]} in Eagle package coords (mm)."""
import json, xml.etree.ElementTree as ET

t = ET.parse('eagle/ISP1807LR_Int.lbr')
pads = {}
for pkg in t.getroot().iter('package'):
    if pkg.get('name') != 'ISP1807-LR':
        continue
    for s in pkg.findall('smd'):
        pads[s.get('name')] = [round(float(s.get('x')), 4), round(float(s.get('y')), 4),
                               round(float(s.get('dx')), 4), round(float(s.get('dy')), 4)]
json.dump(pads, open('official-pads.json', 'w'), indent=1, sort_keys=lambda k: int(k))
xs = [v[0] for v in pads.values()]; ys = [v[1] for v in pads.values()]
print('official pads:', len(pads))
print('x range', min(xs), max(xs), ' y range', min(ys), max(ys))
print('sizes:', sorted({(v[2], v[3]) for v in pads.values()}))
