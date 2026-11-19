"""Via-pad audit, different-net only (the #288 gate form).

Reuses the donor audit's analytic signed-distance (s31_audit.py, itself a
copy of the Rev.3 audit extended for ROUNDRECT) but skips same-net pairs:
a via stacked on its own net's pad is a valid junction, not a clearance
case. Reports the global different-net minimum and every site < 0.125.
"""
import json
import math
import sys
from pathlib import Path

import pcbnew as p

sys.path.insert(0, str(Path(__file__).parent))
from common import *  # noqa: F401,F403 (donor helper module)

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = p.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
mm = p.ToMM

pads = []
for f in b.GetFootprints():
    for q in f.Pads():
        if q.GetAttribute() == p.PAD_ATTRIB_NPTH or not any(q.IsOnLayer(l) for l in [p.F_Cu, p.B_Cu]):
            continue
        pads.append((f.GetReference(), q))

def signed_distance(q, pos):
    dx, dy = mm(pos.x - q.GetPosition().x), mm(pos.y - q.GetPosition().y)
    theta = math.radians(q.GetOrientationDegrees())
    x = dx * math.cos(theta) - dy * math.sin(theta)
    y = dx * math.sin(theta) + dy * math.cos(theta)
    w, h = mm(q.GetSize().x), mm(q.GetSize().y)
    s = q.GetShape()
    if s in (p.PAD_SHAPE_RECT, p.PAD_SHAPE_ROUNDRECT):
        a, c = abs(x) - w / 2, abs(y) - h / 2
        return math.hypot(max(a, 0), max(c, 0)) + min(max(a, c), 0)
    if s == p.PAD_SHAPE_CIRCLE:
        return math.hypot(x, y) - w / 2
    if s == p.PAD_SHAPE_OVAL:
        return math.hypot(max(abs(x) - max(w - h, 0) / 2, 0),
                          max(abs(y) - max(h - w, 0) / 2, 0)) - min(w, h) / 2
    raise AssertionError(('unsupported shape', int(s)))

rows = []
for t in b.GetTracks():
    if not isinstance(t, p.PCB_VIA):
        continue
    pos = t.GetPosition()
    r = mm(t.GetWidth(p.F_Cu)) / 2
    vnet = t.GetNetname()
    best = None
    for ref, q in pads:
        if q.GetNetname() == vnet:
            continue
        gap = signed_distance(q, pos) - r
        if best is None or gap < best[0]:
            best = (gap, ref, q.GetNumber(), q.GetNetname())
    rows.append({'via_net': vnet, 'x': round(mm(pos.x), 3), 'y': round(mm(pos.y), 3),
                 'min_diffnet_gap_mm': round(best[0], 4), 'nearest_pad': f'{best[1]}.{best[2]}',
                 'pad_net': best[3]})
rows.sort(key=lambda r: r['min_diffnet_gap_mm'])
out = {'via_count': len(rows),
       'global_min_diffnet_mm': rows[0]['min_diffnet_gap_mm'],
       'sites_below_0.125': [r for r in rows if r['min_diffnet_gap_mm'] < 0.125],
       'sites_below_0.100': [r for r in rows if r['min_diffnet_gap_mm'] < 0.100]}
(TREE / 'via-audit-s2' / 'via-pad-diffnet.json').write_text(json.dumps(out, indent=1))
print('vias:', len(rows), 'global different-net min:', out['global_min_diffnet_mm'])
print('below 0.125:', len(out['sites_below_0.125']), 'below 0.100:', len(out['sites_below_0.100']))
for r in out['sites_below_0.125'][:12]:
    print('  ', r)
