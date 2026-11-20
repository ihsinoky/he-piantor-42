import pcbnew as p
from collections import defaultdict
def mm(v): return v / 1e6
b = p.LoadBoard('.issue292-runtime/wmain-work.kicad_pcb')
# nodes: (layer, x, y) for track endpoints; vias connect all layers at (x,y); pads are terminals
adj = defaultdict(list)
def key(l, x, y): return (l, round(x, 2), round(y, 2))
for t in b.GetTracks():
    if t.GetNetname() != 'PAD_SCL': continue
    if isinstance(t, p.PCB_VIA):
        q = t.GetPosition(); c = (mm(q.x), mm(q.y))
        for l1 in (0, 4, 6, 31):
            for l2 in (0, 4, 6, 31):
                if l1 != l2: adj[key(l1, *c)].append(key(l2, *c))
    else:
        s, e = t.GetStart(), t.GetEnd()
        a, bb = (mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))
        adj[key(t.GetLayer(), *a)].append(key(t.GetLayer(), *bb))
        adj[key(t.GetLayer(), *bb)].append(key(t.GetLayer(), *a))
# terminals: pads
terms = {}
for f in b.GetFootprints():
    for pad in f.Pads():
        if pad.GetNetname() == 'PAD_SCL':
            q = pad.GetPosition()
            terms[f"{f.GetReference()}.{pad.GetNumber()}"] = (round(mm(q.x), 2), round(mm(q.y), 2))
print('terminals', terms)
# BFS from U1.3 on F
start = key(0, *terms['U1.3'])
seen = {start}; stack = [start]; hops = []
while stack:
    cur = stack.pop()
    for nb in adj[cur]:
        if nb not in seen:
            seen.add(nb); stack.append(nb)
            if nb[0] != cur[0]: hops.append((cur, nb))
print('reachable nodes:', len(seen), 'layer hops:', [(h[0], h[1][0]) for h in hops])
tgt = terms['JPAD.3']
print('JPAD.3 reached on any layer:', any(key(l, *tgt) in seen for l in (0, 4, 6, 31)))
