#!/usr/bin/env python3
"""Generate wmain.pretty/ISP1807-LR.kicad_mod from Insight SiP OFFICIAL CAD.
Pad data: maker's Altium PcbLib read via KiCad 9 import (altium-pads.json),
recentred on the pad-bbox centre (= package centre). Verified against the
maker's Eagle library, the maker's TB gerber, and DS1807 R19 §3/§4.3 —
see PROVENANCE.md. Frame: datasheet TOP VIEW, pin 1 NW, antenna edge +Y."""
import json
from pathlib import Path

E = Path(__file__).resolve().parent
TREE = E.parent.parent/'hardware/kicad/qualification/issue-292-wmain'
LIB = TREE/'wmain.pretty'

alt = {r[0]: r[1:] for r in json.load(open(E/'altium-pads.json'))}
xs = [v[0] for v in alt.values()]; ys = [v[1] for v in alt.values()]
cx, cy = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2
pads = {k: (round(v[0]-cx, 3), round(v[1]-cy, 3), v[2], v[3]) for k, v in alt.items()}
assert len(pads) == 78
json.dump(pads, open(E.parent/'isp1807-official-pads.json', 'w'), indent=0)

def fp_head(name, descr):
    return (f'(footprint "{name}"\n\t(version 20240108)\n\t(generator "pcbnew")\n'
            f'\t(generator_version "9.0")\n\t(layer "F.Cu")\n\t(descr "{descr}")\n\t(attr smd)\n')

def refval():
    return ('\t(property "Reference" "REF**"\n\t\t(at 0 -3 0)\n\t\t(layer "F.SilkS")\n\t\t(effects (font (size 1 1) (thickness 0.15)))\n\t)\n'
            '\t(property "Value" ""\n\t\t(at 0 3 0)\n\t\t(layer "F.Fab")\n\t\t(effects (font (size 1 1) (thickness 0.15)))\n\t)\n')

def rect_lines(cx_, cy_, hx, hy, layer='F.SilkS', w=0.12):
    pts = [(-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy), (-hx, -hy)]
    s = ''
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        s += (f'\t(fp_line\n\t\t(start {cx_+x1:.3f} {cy_+y1:.3f})\n\t\t(end {cx_+x2:.3f} {cy_+y2:.3f})\n'
              f'\t\t(stroke (width {w}) (type solid))\n\t\t(layer "{layer}")\n\t)\n')
    return s

descr = ('Insight SiP ISP1807-LR LGA-78, OFFICIAL maker CAD (Altium library, '
         'insightsip.com fichiers_insightsip/pdf/ble/ISP1807, zip SHA-256 14fa64eb...; '
         'triangulated vs maker Eagle lib + TB gerber + DS1807 R19 S3/S4.3, see '
         '.issue292-runtime/official-cad/PROVENANCE.md). TOP VIEW: pin 1 NW, '
         'antenna edge +Y (NC ring 65-78 side). Pads 65-78 = NC, isolated mechanical pads.')
s = fp_head('ISP1807-LR', descr) + refval()
s += rect_lines(0, 0, 4.0, 4.0)
# pin-1 marker at NW (official frame; the derived fp had it SW in its frame)
s += ('\t(fp_circle\n\t\t(center -4.6 -4.6)\n\t\t(end -4.3 -4.6)\n'
      '\t\t(stroke (width 0.12) (type solid))\n\t\t(fill none)\n\t\t(layer "F.SilkS")\n\t)\n')
for num in sorted(pads, key=lambda z: int(z)):
    x, y, sx, sy = pads[num]
    s += (f'\t(pad "{num}" smd rect\n\t\t(at {x:.3f} {y:.3f})\n\t\t(size {sx:.3f} {sy:.3f})\n'
          f'\t\t(layers "F.Cu" "F.Paste" "F.Mask")\n\t\t(solder_mask_margin 0.05)\n\t)\n')
s += ')\n'
(LIB/'ISP1807-LR.kicad_mod').write_text(s)
print('wrote', LIB/'ISP1807-LR.kicad_mod', 'pads:', len(pads), 'centre offset was', cx, cy)
