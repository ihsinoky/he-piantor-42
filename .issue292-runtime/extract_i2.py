"""BFS on one layer from a start point to a target point (both on NET's copper),
emit the path as track segments. Obstacles: other nets buffered 0.075.
Env: P_NET, P_LAY, P_START 'x,y', P_TARGET 'x,y'. Saves the board."""
import sys, os
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
import pcbnew as p
from shapely.strtree import STRtree
from shapely.geometry import Point
from collections import deque

NET = os.environ.get('P_NET', 'PAD_SCL'); LAY = os.environ.get('P_LAY', 'I2')
SX, SY = [float(v) for v in os.environ['P_START'].split(',')]
TX, TY = [float(v) for v in os.environ['P_TARGET'].split(',')]
obs = [s2.buffer(0.075) for n2, s2 in all_obs(LAY) if n2 != NET]
tree_u = STRtree(obs)
OUTL_E = OUTLINE.buffer(-0.575)
STEP = float(os.environ.get('P_STEP', '0.05'))
start = (round(SX / STEP), round(SY / STEP))
target = (round(TX / STEP), round(TY / STEP))
par = {start: None}
dq = deque([start])
found = False
while dq:
    i, j = dq.popleft()
    if abs(i - target[0]) <= 2 and abs(j - target[1]) <= 2:
        target = (i, j); found = True; break
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ni, nj = i + di, j + dj
        if (ni, nj) in par: continue
        pt = Point(ni * STEP, nj * STEP)
        if not OUTL_E.contains(pt): continue
        if len(tree_u.query(pt)) > 0: continue
        par[(ni, nj)] = (i, j); dq.append((ni, nj))
if not found:
    print('EXTRACT_I2: no path'); sys.exit(1)
cells = []
c = target
while c is not None:
    cells.append(c); c = par[c]
cells.reverse()
pts = [(i * STEP, j * STEP) for i, j in cells]
# merge collinear runs
segs = []
a = pts[0]; prev_dir = None
for k in range(1, len(pts)):
    d = (round(pts[k][0] - pts[k - 1][0], 3), round(pts[k][1] - pts[k - 1][1], 3))
    if prev_dir is not None and d != prev_dir:
        segs.append((a, pts[k - 1])); a = pts[k - 1]
    prev_dir = d
segs.append((a, pts[-1]))
b = p.LoadBoard(DST)
netobj = b.FindNet(NET)
LAYID = {'F': p.F_Cu, 'I2': p.In2_Cu, 'B': p.B_Cu}
for (x1, y1), (x2, y2) in segs:
    t = p.PCB_TRACK(b)
    t.SetNet(netobj); t.SetLayer(LAYID[LAY]); t.SetWidth(int(0.05 * 1e6))
    t.SetStart(p.VECTOR2I(int(x1 * 1e6), int(y1 * 1e6)))
    t.SetEnd(p.VECTOR2I(int(x2 * 1e6), int(y2 * 1e6)))
    b.Add(t)
p.SaveBoard(DST, b)
print(f'EXTRACT_I2 {NET}: path {len(cells)} cells -> {len(segs)} segments on {LAY}')
