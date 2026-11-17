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
s = attach(adj, pad_node('J_WING', 1))
cs = comp(s)
print('source comp size', len(cs))
for mux in ('U_MUX_A', 'U_MUX_C'):
    t = attach(adj, pad_node(mux, 13))
    ct = comp(t)
    xs = [n[0] for n in ct]; ys = [n[1] for n in ct]
    print(mux, 'target node', t, 'comp size', len(ct), 'bbox x %.1f..%.1f y %.1f..%.1f' % (min(xs), max(xs), min(ys), max(ys)), 'in source comp:', t in cs)
