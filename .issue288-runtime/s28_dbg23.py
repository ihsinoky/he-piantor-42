import math, sys
from pathlib import Path
import pcbnew
MM = 1e6
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
for t in list(b.GetTracks()):
    if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() == 'VIN_SRC':
        p = t.GetPosition()
        print(f'via ({p.x/MM:.3f},{p.y/MM:.3f}) drill={t.GetDrill()/MM:.3f} width={t.GetWidth(pcbnew.F_Cu)/MM:.3f} dist_to_npth={math.hypot(p.x/MM-147.11, p.y/MM-133.4):.3f}')
