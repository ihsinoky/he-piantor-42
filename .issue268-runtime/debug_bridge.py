exec(open('.issue268-runtime/bridge_base.py').read())
from collections import deque
net = 'GND'; width = 0.3
comps = [c for c in components(net) if any(it.kind == 'pad' for it in c)]
comps.sort(key=lambda c: -len(c))
print('pad comps:', [(len(c), sorted({it.obj.GetParentFootprint().GetReference() + '.' + it.obj.GetNumber() for it in c if it.kind == 'pad'} and {''}) ) for c in comps])
for i, c in enumerate(comps):
    labs = []
    for it in c:
        if it.kind == 'pad':
            fp = it.obj.GetParentFootprint()
            labs.append(fp.GetReference() + '.' + it.obj.GetNumber())
    print(i, 'items', len(c), 'pads', sorted(set(labs))[:8])
target = comps[0]; source = comps[-1]
blocked = raster_blocked(net, width); viablocked = raster_blocked(net, width, via=True)
goal = goal_mask(target, width); startmask = goal_mask(source, width)
print('goal cells F/B:', int(goal[0].sum()), int(goal[1].sum()), 'start cells F/B:', int(startmask[0].sum()), int(startmask[1].sum()))
print('start blocked F/B:', int((startmask[0] & blocked[0]).sum()), int((startmask[1] & blocked[1]).sum()))
print('goal blocked F/B:', int((goal[0] & blocked[0]).sum()), int((goal[1] & blocked[1]).sum()))
# BFS from startmask
seen = np.zeros((2, NY, NX), bool)
dq = deque()
idx = np.argwhere(np.stack([startmask[0], startmask[1]], axis=0))
for l, y, x in idx.tolist():
    if not blocked[l][y, x] and not seen[l, y, x]:
        seen[l, y, x] = True; dq.append((x, y, l))
while dq:
    x, y, l = dq.popleft()
    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
        nx_, ny_ = x+dx, y+dy
        if 0 <= nx_ < NX and 0 <= ny_ < NY and not seen[l, ny_, nx_] and not blocked[l][ny_, nx_]:
            if dx and dy and (blocked[l][y, nx_] or blocked[l][ny_, x]): continue
            seen[l, ny_, nx_] = True; dq.append((nx_, ny_, l))
    if not viablocked[0][y, x] and not viablocked[1][y, x] and not seen[1-l, y, x]:
        seen[1-l, y, x] = True; dq.append((x, y, 1-l))
print('reachable:', int(seen.sum()), 'goal reached F/B:', int((goal[0] & seen[0]).sum()), int((goal[1] & seen[1]).sum()))
