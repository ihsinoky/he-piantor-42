"""Surgical fixes on the KRT-routed board (sexpr token model: numbers are
strings, quoted strings are ('str', v) tuples)."""
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

tree = parse((E/'wmain-routed3.kicad_pcb').read_text())
netcode = {}
for c in tree[1:]:
    if isinstance(c, list) and c and c[0] == 'net':
        netcode[val(c[2])] = val(c[1])
STRIP = {'FB_3V3', 'SYS_3V3', 'VBAT_SENSE', 'BTN'}
codes = {netcode[n] for n in STRIP}

def seg_net(node):
    n = child(node, 'net')
    return val(n[1]) if n else None

def seg_mid(node):
    s, e = child(node, 'start'), child(node, 'end')
    x1, y1, x2, y2 = float(s[1]), float(s[2]), float(e[1]), float(e[2])
    return ((x1 + x2) / 2, (y1 + y2) / 2, abs(x1 - x2) + abs(y1 - y2))

removed = {'strip': 0, 'junk': 0}
out = []
for c in tree:
    if isinstance(c, list) and c and c[0] in ('segment', 'via'):
        nc = seg_net(c)
        if nc in codes:
            removed['strip'] += 1
            continue
        if c[0] == 'segment':
            mx, my, ln = seg_mid(c)
            if nc == netcode['VBAT_GATE_M'] and abs(mx - 71.2) < 0.3 and abs(my - 123.875) < 0.3 and ln < 0.6:
                removed['junk'] += 1
                continue
            if nc == netcode['SWDCLK'] and ln < 0.1 and abs(mx - 79.8) < 0.3 and abs(my - 127.9) < 0.3:
                removed['junk'] += 1
                continue
    if isinstance(c, list) and c and c[0] == 'footprint':
        for x in c:
            if isinstance(x, list) and x and x[0] == 'property' and len(x) > 2 \
               and val(x[1]) == 'Reference' and val(x[2]) == 'RFB2':
                at = child(c, 'at')
                at[1], at[2] = '96.2', '97.3'
                if len(at) > 3:
                    at[3] = '0'
    out.append(c)

def stub(x, y1, y2, netname):
    return ['segment', ['start', str(x), str(y1)], ['end', str(x), str(y2)],
            ['width', '0.1'], ['layer', ('str', 'F.Cu')],
            ['net', netcode[netname]], ['uuid', ('str', str(uuid.uuid4()))]]
out.append(stub(71.2, 128.425, 126.4, 'BTN'))
out.append(stub(75.125, 128.45, 126.4, 'VBAT_SENSE'))
(E/'wmain-fixed.kicad_pcb').write_text(ser(out) + '\n')
print('removed:', removed, '; RFB2 moved; stubs added')
