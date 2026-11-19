import sys
from pathlib import Path
import pcbnew
MM = 1e6
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
for t in list(b.GetTracks()):
    if t.Type() == pcbnew.PCB_VIA_T:
        p = t.GetPosition()
        if 77 < p.x / MM < 84 and 118 < p.y / MM < 125:
            print(f'VIA {t.GetNetname()} ({p.x/MM:.2f},{p.y/MM:.2f})')
    else:
        s, e = t.GetStart(), t.GetEnd()
        if (77 < s.x / MM < 84 and 118 < s.y / MM < 125) or (77 < e.x / MM < 84 and 118 < e.y / MM < 125):
            lay = 'F' if t.GetLayer() == pcbnew.F_Cu else 'B'
            if t.GetNetname() in ('H_A0_RAW', 'GND', 'MUX_A0'):
                print(f'{t.GetNetname()} {lay} ({s.x/MM:.2f},{s.y/MM:.2f})->({e.x/MM:.2f},{e.y/MM:.2f})')
for fp in list(b.GetFootprints()):
    p = fp.GetPosition()
    if 77 < p.x / MM < 84 and 118 < p.y / MM < 125:
        print('FP', fp.GetReference(), (round(p.x / MM, 2), round(p.y / MM, 2)))
        for pad in fp.Pads():
            pp = pad.GetPosition()
            print('   pad', pad.GetNumber(), pad.GetNetname(), (round(pp.x / MM, 2), round(pp.y / MM, 2)))
