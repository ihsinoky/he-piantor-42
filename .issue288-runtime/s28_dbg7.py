import heapq, math, sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
import s24_router
from s24_router import Obstacles

s24_router.CLEAR = 0.10
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
obs = Obstacles(b)
netcode = b.FindNet('EN_A').GetNetCode()
GRID = 0.25
sx, sy, sl = 50.25, 90.7, 0
ex, ey, el = 50.25, 74.7, 0
x0, x1, y0, y1 = 38.25, 62.25, 62.7, 102.7
nx = int((x1 - x0) / GRID) + 1; ny = int((y1 - y0) / GRID) + 1
def cell_of(x, y): return (int(round((x - x0) / GRID)), int(round((y - y0) / GRID)))
def xy_of(i, j): return (x0 + i * GRID, y0 + j * GRID)
si, sj = cell_of(sx, sy); ei, ej = cell_of(ex, ey)
print('start', si, sj, 'goal', ei, ej, 'grid', nx, ny)
def heuristic(i, j, l): return math.hypot(i - ei, j - ej) + (0 if l == el else 3)
start_state = (si, sj, sl); goal_cells = {(ei, ej, el)}
open_heap = [(heuristic(si, sj, sl), 0.0, start_state)]
came = {start_state: None}; gscore = {start_state: 0.0}
DIRS = [(1,0,1.0),(-1,0,1.0),(0,1,1.0),(0,-1,1.0),(1,1,1.414),(1,-1,1.414),(-1,1,1.414),(-1,-1,1.414)]
expanded = 0; mind = 1e9; minstate = None
while open_heap:
    _, g, state = heapq.heappop(open_heap)
    if g > gscore.get(state, 1e18) + 1e-9: continue
    if state in goal_cells: break
    expanded += 1
    i, j, l = state
    d = math.hypot(i - ei, j - ej)
    if d < mind: mind, minstate = d, state
    x, y = xy_of(i, j)
    for di, dj, cost in DIRS:
        ni, nj = i + di, j + dj
        if not (0 <= ni < nx and 0 <= nj < ny): continue
        nstate = (ni, nj, l)
        if nstate in came and gscore.get(nstate, 1e18) <= g + cost: continue
        px, py = xy_of(ni, nj)
        if nstate not in goal_cells and obs.blocked(px, py, l, netcode, 0.05): continue
        came[nstate] = state; gscore[nstate] = g + cost
        heapq.heappush(open_heap, (g + cost + heuristic(ni, nj, l), g + cost, nstate))
    nstate = (i, j, 1 - l)
    if not (nstate in came and gscore.get(nstate, 1e18) <= g + 4):
        if not obs.blocked(x, y, 0, netcode, 0.30, via=True) and not obs.blocked(x, y, 1, netcode, 0.30, via=True):
            came[nstate] = state; gscore[nstate] = g + 4
            heapq.heappush(open_heap, (g + 4 + heuristic(i, j, 1 - l), g + 4, nstate))
print('expanded', expanded, 'visited', len(came), 'closest state', minstate, 'dist cells', mind,
      'at xy', xy_of(minstate[0], minstate[1]) if minstate else None)

print('--- goal neighbourhood audit (cells around goal 48,48)')
for dj in (-2, -1, 0, 1, 2):
    for di in (-2, -1, 0, 1, 2):
        i, j = ei + di, ej + dj
        x, y = xy_of(i, j)
        st = []
        for l in (0, 1):
            st.append('V' if (i, j, l) in came else '-')
        bf = obs.blocked(x, y, 0, netcode, 0.05)
        bb = obs.blocked(x, y, 1, netcode, 0.05)
        vf = obs.blocked(x, y, 0, netcode, 0.30, via=True)
        print(f'  cell ({i},{j}) xy=({x:.2f},{y:.2f}) visited F/B={st[0]}{st[1]} blockedF={bf} blockedB={bb} viaBlocked={vf}')
