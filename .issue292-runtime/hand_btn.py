"""Hand-route BTN (the one net KRT could not complete):
delete KRT's west stub at the module pad; escape north on F.Cu, via to
In2.Cu, run north/east on In2 to the existing SW1 through-via at
(100.8, 84.0)."""
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

tree = parse((E/'wmain-routed4.kicad_pcb').read_text())
netcode = {}
for c in tree[1:]:
    if isinstance(c, list) and c and c[0] == 'net':
        netcode[val(c[2])] = val(c[1])
BTN = netcode['BTN']
out = []
removed = 0
for c in tree:
    if isinstance(c, list) and c and c[0] == 'segment':
        n = child(c, 'net')
        if n and val(n[1]) == BTN:
            s, e = child(c, 'start'), child(c, 'end')
            pts = {(round(float(s[1]), 2), round(float(s[2]), 2)),
                   (round(float(e[1]), 2), round(float(e[2]), 2))}
            if pts == {(71.2, 128.43), (70.85, 128.42)}:
                removed += 1
                continue
    out.append(c)

def seg(x1, y1, x2, y2, layer):
    return ['segment', ['start', str(x1), str(y1)], ['end', str(x2), str(y2)],
            ['width', '0.1'], ['layer', ('str', layer)], ['net', BTN],
            ['uuid', ('str', str(uuid.uuid4()))]]
out.append(seg(71.2, 128.425, 71.2, 126.6, 'F.Cu'))
out.append(['via', ['at', '71.2', '126.6'], ['size', '0.6'], ['drill', '0.3'],
            ['layers', ('str', 'F.Cu'), ('str', 'B.Cu')], ['net', BTN],
            ['uuid', ('str', str(uuid.uuid4()))]])
out.append(seg(71.2, 126.6, 71.2, 101.0, 'In2.Cu'))
out.append(seg(71.2, 101.0, 98.6, 101.0, 'In2.Cu'))
out.append(seg(98.6, 101.0, 100.8, 84.0, 'In2.Cu'))
(E/'wmain-final.kicad_pcb').write_text(ser(out) + '\n')
print('stub removed:', removed, '; BTN hand route added')
