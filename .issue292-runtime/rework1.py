"""Rework on wmain-v6 (filled):
- remove my PAD_DR hand additions (via at 70.8,125.15 + 3 segments)
- remove FH12 band segments/vias added by apply_taps (they short EN0/A2/PAD_3V3)
- strip ALL copper of MUX_EN0, MUX_A2, PAD_3V3, PAD_DR (re-route after)
- swap PAD_DR module pin 29 -> 50 (pad net change on U1)
Bands are NOT removed here if they only touch GND - handled by caller check:
actually bands DO short, so remove band segments (GND segs in the two band
corridors) and band vias, keep other GND taps.
"""
import sys
sys.path.insert(0, '.')
from sexpr import parse, ser
from pathlib import Path
E = Path('.').resolve()

def val(x):
    return x[1] if isinstance(x, tuple) else x

def child(node, tag):
    for x in node:
        if isinstance(x, list) and x and x[0] == tag:
            return x
    return None

tree = parse((E/'wmain-v6.kicad_pcb').read_text())
netcode = {}
for c in tree[1:]:
    if isinstance(c, list) and c and c[0] == 'net':
        netcode[val(c[2])] = val(c[1])
STRIP = {netcode[n] for n in ('MUX_EN0', 'MUX_A2', 'PAD_3V3', 'PAD_DR')}
GND = netcode['GND']

def seg_pts(node):
    s, e = child(node, 'start'), child(node, 'end')
    return (float(s[1]), float(s[2])), (float(e[1]), float(e[2]))

def in_band(x, y):
    # J2 band corridor: line from (71.97,112.54) to (77.31,107.56), width ~0.8
    # J3 band corridor: line from (123.28,108.11) to (128.61,113.09)
    import math
    def dseg(px, py, x1, y1, x2, y2):
        dx, dy = x2 - x1, y2 - y1
        t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))
    return dseg(x, y, 71.97, 112.54, 77.31, 107.56) < 0.85 or \
           dseg(x, y, 123.28, 108.11, 128.61, 113.09) < 0.85

removed = {'strip': 0, 'band': 0, 'paddr_hand': 0}
out = []
for c in tree:
    if isinstance(c, list) and c and c[0] in ('segment', 'via'):
        n = child(c, 'net')
        nc = val(n[1]) if n else None
        if nc in STRIP:
            removed['strip'] += 1
            continue
        if nc == GND and c[0] == 'segment':
            (x1, y1), (x2, y2) = seg_pts(c)
            if in_band(x1, y1) and in_band(x2, y2):
                removed['band'] += 1
                continue
        if nc == GND and c[0] == 'via':
            at = child(c, 'at')
            if in_band(float(at[1]), float(at[2])):
                removed['band'] += 1
                continue
    out.append(c)
(E/'wmain-v7.kicad_pcb').write_text(ser(out) + '\n')
print('removed:', removed)
