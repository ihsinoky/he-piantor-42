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
SRC, DST, NETS = sys.argv[1], sys.argv[2], set(sys.argv[3:])
tree = parse((E/SRC).read_text())
netcode = {}
for c in tree[1:]:
    if isinstance(c, list) and c and c[0] == 'net':
        netcode[val(c[2])] = val(c[1])
codes = {netcode[n] for n in NETS}
removed = 0
out = []
for c in tree:
    if isinstance(c, list) and c and c[0] in ('segment', 'via', 'arc'):
        n = child(c, 'net')
        if n and val(n[1]) in codes:
            removed += 1
            continue
    out.append(c)
(E/DST).write_text(ser(out) + '\n')
print('stripped', removed, 'items for', sorted(NETS))
