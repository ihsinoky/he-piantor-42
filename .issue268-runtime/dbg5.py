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
print('source-comp nodes x 93..103, y 119..126:')
for n in sorted(cs):
    if 93 <= n[0] <= 103 and 119 <= n[1] <= 126: print('  ', n)
print('adj nodes (not in comp) same box:')
for n in sorted(adj):
    if 93 <= n[0] <= 103 and 119 <= n[1] <= 126 and n not in cs: print('  ', n, 'deg', len(adj[n]))
