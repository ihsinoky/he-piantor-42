"""Strip all non-GND copper intersecting the two FH12 field rects from
wmain-v12-final; report the affected nets for re-routing."""
import sys
sys.path.insert(0, '.')
from sexpr import parse, ser
from pathlib import Path
E = Path('.').resolve()
RECTS = [(66, 86, 102, 121), (114, 134, 102, 121)]

def val(x): return x[1] if isinstance(x, tuple) else x
def child(node, tag):
    for x in node:
        if isinstance(x, list) and x and x[0] == tag: return x

def seg_rect(x1, y1, x2, y2, r):
    # sample + endpoint test (segments here are short)
    for t in (0, 0.25, 0.5, 0.75, 1.0):
        x, y = x1 + t * (x2 - x1), y1 + t * (y2 - y1)
        if r[0] <= x <= r[1] and r[2] <= y <= r[3]:
            return True
    return False

tree = parse((E/'wmain-v12-final.kicad_pcb').read_text())
netname = {}
for c in tree[1:]:
    if isinstance(c, list) and c and c[0] == 'net':
        netname[val(c[1])] = val(c[2])
GND = [k for k, v in netname.items() if v == 'GND'][0]
out = []
affected = set()
rm = 0
for c in tree:
    if isinstance(c, list) and c and c[0] in ('segment', 'via'):
        n = child(c, 'net')
        nc = val(n[1]) if n else None
        if nc != GND:
            hit = False
            if c[0] == 'segment':
                s, e = child(c, 'start'), child(c, 'end')
                hit = any(seg_rect(float(s[1]), float(s[2]), float(e[1]), float(e[2]), r) for r in RECTS)
            else:
                at = child(c, 'at')
                hit = any(r[0] <= float(at[1]) <= r[1] and r[2] <= float(at[2]) <= r[3] for r in RECTS)
            if hit:
                affected.add(netname.get(nc, nc))
                rm += 1
                continue
    out.append(c)
(E/'wmain-v13.kicad_pcb').write_text(ser(out) + '\n')
print('removed:', rm)
print('affected nets:', sorted(affected))
