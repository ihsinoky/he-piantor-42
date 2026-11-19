import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, _pad_signed_dist, _seg_dist

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
obs = Obstacles(b)
names = {n.GetNetCode(): n.GetNetname() for n in b.GetNetsByName().values()}
def probe(net, x, y):
    nc = b.FindNet(net).GetNetCode()
    hits = []
    for pad in obs.pads:
        if pad[7] == nc or not pad[8]:
            continue
        sd = _pad_signed_dist(pad, x, y)
        if sd < 0.3:
            hits.append((round(sd, 3), names.get(pad[7]), 'pad'))
    for (ax, ay, bx, by, hw, snc, lay) in obs.segs:
        if snc == nc or lay != 0:
            continue
        d = _seg_dist(x, y, ax, ay, bx, by) - hw
        if d < 0.3:
            hits.append((round(d, 3), names.get(snc), 'seg'))
    print((x, y), sorted(hits)[:4])
for x in (136.0, 135.5, 135.0, 134.6):
    probe('H_B3_RAW', x, 74.3)
# HA5 RAW wrap: print H_A5_RAW segs near (117,107)
for (ax, ay, bx, by, hw, snc, lay) in obs.segs:
    if names.get(snc) == 'H_A5_RAW' and lay == 0 and 113 < ax < 122 and 103 < ay < 112:
        print('H_A5_RAW seg', (round(ax, 2), round(ay, 2)), '->', (round(bx, 2), round(by, 2)))
