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
nc = b.FindNet('EN_A').GetNetCode()
GRID = 0.25
sx, sy, sl = 50.25, 90.7, 0
ex, ey, el = 50.25, 74.7, 0
x0 = max(min(sx, ex) - 4.0, obs.bbox[0] + 0.2); x1 = min(max(sx, ex) + 4.0, obs.bbox[2] - 0.2)
y0 = max(min(sy, ey) - 4.0, obs.bbox[1] + 0.2); y1 = min(max(sy, ey) + 4.0, obs.bbox[3] - 0.2)
print('window', x0, x1, y0, y1, 'bbox', obs.bbox)
nx = int((x1 - x0) / GRID) + 1; ny = int((y1 - y0) / GRID) + 1
print('cells', nx, ny)
def cell_of(x, y): return (int(round((x - x0) / GRID)), int(round((y - y0) / GRID)))
def xy_of(i, j): return (x0 + i * GRID, y0 + j * GRID)
si, sj = cell_of(sx, sy); ei, ej = cell_of(ex, ey)
print('start cell', si, sj, xy_of(si, sj), 'goal cell', ei, ej, xy_of(ei, ej))
print('goal blocked?', obs.blocked(ex, ey, 0, nc, 0.05), 'start blocked?', obs.blocked(sx, sy, 0, nc, 0.05))
# count free cells in window on F
free = sum(1 for i in range(nx) for j in range(ny) if not obs.blocked(*xy_of(i, j), 0, nc, 0.05))
print('free F cells:', free, 'of', nx * ny)
