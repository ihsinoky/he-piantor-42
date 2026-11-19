import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, _pad_signed_dist, _seg_dist

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
obs = Obstacles(b)
nc = b.FindNet('EN_A').GetNetCode()
names = {n.GetNetCode(): n.GetNetname() for n in b.GetNetsByName().values()}
for (x, y) in [(50.5, 74.7), (51.0, 74.7), (51.5, 74.7), (49.75, 74.7), (50.25, 75.7), (50.25, 73.7)]:
    hits = []
    for pad in obs.pads:
        if pad[7] == nc or not pad[8]:
            continue
        sd = _pad_signed_dist(pad, x, y)
        if sd < 0.4:
            hits.append((round(sd, 3), names.get(pad[7]), 'pad'))
    for (ax, ay, bx, by, hw, snc, lay) in obs.segs:
        if snc == nc or lay != 0:
            continue
        d = _seg_dist(x, y, ax, ay, bx, by) - hw
        if d < 0.4:
            hits.append((round(d, 3), names.get(snc), 'seg'))
    print((x, y), sorted(hits)[:5])
