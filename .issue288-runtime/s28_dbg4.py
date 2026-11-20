import heapq, math, sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
import s24_router
from s24_router import Obstacles

s24_router.CLEAR = 0.13
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
obs = Obstacles(b)
netcode = b.FindNet('EN_A').GetNetCode()
GRID = 0.25
sx, sy, sl = 50.25, 90.7, 0
ex, ey, el = 50.25, 74.7, 0
my_half = 0.05
x0 = min(sx, ex) - 4.0; x1 = max(sx, ex) + 4.0
y0 = min(sy, ey) - 4.0; y1 = max(sy, ey) + 4.0
x0 = max(x0, obs.bbox[0] + 0.2); y0 = max(y0, obs.bbox[1] + 0.2)
x1 = min(x1, obs.bbox[2] - 0.2); y1 = min(y1, obs.bbox[3] - 0.2)
nx = int((x1 - x0) / GRID) + 1; ny = int((y1 - y0) / GRID) + 1
def cell_of(x, y): return (int(round((x - x0) / GRID)), int(round((y - y0) / GRID)))
def xy_of(i, j): return (x0 + i * GRID, y0 + j * GRID)
si, sj = cell_of(sx, sy); ei, ej = cell_of(ex, ey)
def heuristic(i, j, l): return math.hypot(i - ei, j - ej) + (0 if l == el else 3)
start_state = (si, sj, sl); goal_cells = {(ei, ej, el)}
open_heap = [(heuristic(si, sj, sl), 0.0, start_state)]
came = {start_state: None}; gscore = {start_state: 0.0}
DIRS = [(1,0,1.0),(-1,0,1.0),(0,1,1.0),(0,-1,1.0),(1,1,1.414),(1,-1,1.414),(-1,1,1.414),(-1,-1,1.414)]
found = None; expanded = 0; pushed_goal = False
while open_heap:
    _, g, state = heapq.heappop(open_heap)
    if g > gscore.get(state, 1e18) + 1e-9: continue
    if state in goal_cells:
        found = state; break
    expanded += 1
    i, j, l = state
    x, y = xy_of(i, j)
    for di, dj, cost in DIRS:
        ni, nj = i + di, j + dj
        if not (0 <= ni < nx and 0 <= nj < ny): continue
        nstate = (ni, nj, l)
        if nstate in came and gscore.get(nstate, 1e18) <= g + cost: continue
        px, py = xy_of(ni, nj)
        if obs.blocked(px, py, l, netcode, my_half): continue
        came[nstate] = state; gscore[nstate] = g + cost
        if nstate in goal_cells: pushed_goal = True
        heapq.heappush(open_heap, (g + cost + heuristic(ni, nj, l), g + cost, nstate))
    nstate = (i, j, 1 - l)
    if not (nstate in came and gscore.get(nstate, 1e18) <= g + 4):
        if not obs.blocked(x, y, 0, netcode, 0.30, via=True) and not obs.blocked(x, y, 1, netcode, 0.30, via=True):
            came[nstate] = state; gscore[nstate] = g + 4
            heapq.heappush(open_heap, (g + 4 + heuristic(i, j, 1 - l), g + 4, nstate))
print('found:', found, 'expanded:', expanded, 'pushed_goal:', pushed_goal, 'visited:', len(came))
