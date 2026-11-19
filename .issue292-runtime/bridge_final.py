"""Final bridges for the 3 pad-approach gaps + antenna rule-area south
boundary moved to the module body edge (y=128.9; maker wording: exclusion
from the antenna edge to the board edge)."""
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

tree = parse((E/'wmain-v4-routed4.kicad_pcb').read_text())
netcode = {}
for c in tree[1:]:
    if isinstance(c, list) and c and c[0] == 'net':
        netcode[val(c[2])] = val(c[1])

BRIDGES = [('ADC_C', 76.716, 128.65, 76.725, 128.45),
           ('VBAT_SENSE', 75.416, 128.65, 75.425, 128.45),
           ('SWDCLK', 71.15, 125.816, 71.5, 125.825)]
out = list(tree)
for (netname, x1, y1, x2, y2) in BRIDGES:
    out.append(['segment', ['start', str(x1), str(y1)], ['end', str(x2), str(y2)],
                ['width', '0.1'], ['locked', 'yes'], ['layer', ('str', 'F.Cu')],
                ['net', netcode[netname]], ['uuid', ('str', str(uuid.uuid4()))]])

# shrink ANTENNA_KEEP_OUT zones: outline points with y == 127.9 -> 128.9
patched = 0
for c in out:
    if isinstance(c, list) and c and c[0] == 'zone':
        zn = child(c, 'name')
        if zn and val(zn[1]) == 'ANTENNA_KEEP_OUT':
            def walk(node):
                global patched
                if isinstance(node, list):
                    if node and node[0] == 'xy' and len(node) > 2 and abs(float(node[2]) - 127.9) < 0.01:
                        node[2] = '128.9'
                        patched += 1
                    for x in node:
                        walk(x)
            walk(c)
(E/'wmain-v4-final.kicad_pcb').write_text(ser(out) + '\n')
print('bridges added; antenna zone points patched:', patched)
