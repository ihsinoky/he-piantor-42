"""Delete zero-length segments; hand-complete PAD_DR:
F stub to (70.8,125.15), 0.5/0.3 via, B.Cu two-segment run to the
existing B chain end at (81.8,125.9)."""
import sys, uuid
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

tree = parse((E/'wmain-v5-final.kicad_pcb').read_text())
netcode = {}
for c in tree[1:]:
    if isinstance(c, list) and c and c[0] == 'net':
        netcode[val(c[2])] = val(c[1])
PD = netcode['PAD_DR']
out = []
nz = 0
for c in tree:
    if isinstance(c, list) and c and c[0] == 'segment':
        s, e = child(c, 'start'), child(c, 'end')
        if float(s[1]) == float(e[1]) and float(s[2]) == float(e[2]):
            nz += 1
            continue
    out.append(c)

def seg(x1, y1, x2, y2, layer, w='0.1'):
    return ['segment', ['start', str(x1), str(y1)], ['end', str(x2), str(y2)],
            ['width', w], ['locked', 'yes'], ['layer', ('str', layer)],
            ['net', PD], ['uuid', ('str', str(uuid.uuid4()))]]
out.append(seg(71.15, 125.17, 70.8, 125.15, 'F.Cu'))
out.append(['via', ['at', '70.8', '125.15'], ['size', '0.5'], ['drill', '0.3'],
            ['layers', ('str', 'F.Cu'), ('str', 'B.Cu')], ['net', PD],
            ['uuid', ('str', str(uuid.uuid4()))]])
out.append(seg(70.8, 125.15, 76.0, 124.6, 'B.Cu'))
out.append(seg(76.0, 124.6, 81.8, 125.9, 'B.Cu'))
(E/'wmain-v6.kicad_pcb').write_text(ser(out) + '\n')
print('zero-length removed:', nz, '; PAD_DR completed')
