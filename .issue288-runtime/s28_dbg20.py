import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, _pad_signed_dist, _seg_dist

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
obs = Obstacles(b)
nc = b.FindNet('MUXA_OUT').GetNetCode()
names = {n.GetNetCode(): n.GetNetname() for n in b.GetNetsByName().values()}
for (x, y) in [(78.185, 123.86), (78.17, 123.92), (78.20, 123.80)]:
    hits = []
    for pad in obs.pads:
        if pad[7] == nc:
            continue
        sd = _pad_signed_dist(pad, x, y)
        if sd < 0.55:
            hits.append((round(sd, 3), names.get(pad[7]), 'pad', 'F' if pad[8] else '', 'B' if pad[9] else ''))
    for (ax, ay, bx, by, hw, snc, lay) in obs.segs:
        if snc == nc:
            continue
        d = _seg_dist(x, y, ax, ay, bx, by) - hw
        if d < 0.55:
            hits.append((round(d, 3), names.get(snc), f'seg L{lay}'))
    for (vx, vy, r, vnc) in obs.vias:
        if vnc == nc:
            continue
        import math
        d = math.hypot(x - vx, y - vy) - r
        if d < 0.55:
            hits.append((round(d, 3), names.get(vnc), 'via'))
    print((x, y), sorted(hits)[:5])
