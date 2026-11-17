import math
import pcbnew as p
src = open('.issue268-runtime/extract268.py').read()
exec(src.split("res = {}")[0])
adj = build('HALL_5V')
def comp(start):
    seen, stack = set(), [start]
    while stack:
        u = stack.pop()
        if u in seen: continue
        seen.add(u); stack += [v for v, r in adj.get(u, [])]
    return seen
cs = comp(attach(adj, pad_node('J_WING', 1)))
ct = comp(attach(adj, pad_node('U_MUX_C', 13)))
best = (9e9, None, None)
for a in cs:
    for c in ct:
        if a[2] != c[2]: continue
        d = math.hypot(a[0]-c[0], a[1]-c[1])
        if d < best[0]: best = (d, a, c)
print('closest nodes source<->C comp:', best)
xs = [n[0] for n in cs]; ys = [n[1] for n in cs]
print('source comp bbox x %.1f..%.1f y %.1f..%.1f size %d' % (min(xs), max(xs), min(ys), max(ys), len(cs)))
