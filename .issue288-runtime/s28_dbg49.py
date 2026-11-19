import math, sys
from pathlib import Path
import pcbnew
MM = 1e6
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
nets = {b.FindNet(n).GetNetCode() for n in ('HALL_3V3', 'HALL_3V3_SRC')}
print('net codes:', nets)
from collections import Counter
cnt = Counter()
for t in list(b.GetTracks()):
    if t.GetNetCode() in nets:
        cnt['via' if t.Type() == pcbnew.PCB_VIA_T else 'seg'] += 1
print('rail tracks:', dict(cnt))
# degree of the HA0 VCC node in the endpoint graph
target = (49.75, 73.3)
deg = 0
for t in list(b.GetTracks()):
    if t.GetNetCode() not in nets or t.Type() == pcbnew.PCB_VIA_T:
        continue
    s, e = t.GetStart(), t.GetEnd()
    for p in (s, e):
        if (round(p.x / MM, 3), round(p.y / MM, 3)) == target:
            deg += 1
print('HA0 VCC endpoint degree:', deg)
# where does the LDO VOUT pad sit and what touches it
for fp in list(b.GetFootprints()):
    if fp.GetReference() == 'U_LDO':
        for pad in fp.Pads():
            pp = pad.GetPosition()
            print('U_LDO pad', pad.GetNumber(), pad.GetNetname(), (round(pp.x / MM, 3), round(pp.y / MM, 3)))
