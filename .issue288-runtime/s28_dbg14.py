import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
MM = 1e6
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
for t in list(b.GetTracks()):
    if t.Type() != pcbnew.PCB_TRACE_T:
        continue
    s, e = t.GetStart(), t.GetEnd()
    sx, sy, ex, ey = s.x / MM, s.y / MM, e.x / MM, e.y / MM
    if min(sx, ex) < 55 and max(sx, ex) > 45 and min(sy, ey) < 79 and max(sy, ey) > 70:
        lay = 'F' if t.GetLayer() == pcbnew.F_Cu else 'B'
        print(f'{t.GetNetname():12s} {lay} ({sx:.2f},{sy:.2f})->({ex:.2f},{ey:.2f}) w={t.GetWidth()/MM:.2f}')
