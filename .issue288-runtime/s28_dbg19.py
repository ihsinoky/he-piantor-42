import sys
from pathlib import Path
import pcbnew
MM = 1e6
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
def near(x, y):
    return 144 < x < 160 and 100 < y < 118
for t in list(b.GetTracks()):
    if t.Type() == pcbnew.PCB_VIA_T:
        p = t.GetPosition()
        if near(p.x / MM, p.y / MM):
            print(f'VIA {t.GetNetname():10s} ({p.x/MM:.2f},{p.y/MM:.2f})')
    elif t.Type() == pcbnew.PCB_TRACE_T:
        s, e = t.GetStart(), t.GetEnd()
        if near(s.x / MM, s.y / MM) or near(e.x / MM, e.y / MM):
            lay = 'F' if t.GetLayer() == pcbnew.F_Cu else 'B'
            print(f'{t.GetNetname():10s} {lay} ({s.x/MM:.2f},{s.y/MM:.2f})->({e.x/MM:.2f},{e.y/MM:.2f}) w={t.GetWidth()/MM:.2f}')
