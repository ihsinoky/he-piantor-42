import pcbnew as p, math
src = open('.issue268-runtime/extract268.py').read()
exec(src.split("res = {}")[0])
adj = build('HALL_5V')
seen, comps = set(), []
for n in adj:
    if n in seen: continue
    stack, c = [n], set()
    while stack:
        u = stack.pop()
        if u in c: continue
        c.add(u); stack += [v for v, r in adj.get(u, [])]
    seen |= c; comps.append(c)
comps.sort(key=len, reverse=True)
print('components:', [(len(c), ) for c in comps])
for i in range(len(comps)):
    for j in range(i + 1, len(comps)):
        best = (9e9, None, None)
        for a in comps[i]:
            for c in comps[j]:
                if a[2] != c[2]: continue
                d = math.hypot(a[0]-c[0], a[1]-c[1])
                if d < best[0]: best = (d, a, c)
        if best[0] < 3.0: print('comp', i, '<->', j, 'closest', best)
