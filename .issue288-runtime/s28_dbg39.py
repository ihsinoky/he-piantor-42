import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, _pad_signed_dist, _seg_dist

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
obs = Obstacles(b)
names = {n.GetNetCode(): n.GetNetname() for n in b.GetNetsByName().values()}
nc = b.FindNet('H_A0_RAW').GetNetCode()
path = [(79.9, 121.7), (80.3, 121.35), (80.45, 120.75)]
for a, c in zip(path, path[1:]):
    for k in range(11):
        t = k / 10
        x, y = a[0] + (c[0] - a[0]) * t, a[1] + (c[1] - a[1]) * t
        if obs.blocked(x, y, 0, nc, 0.05):
            hits = []
            for pad in obs.pads:
                if pad[7] == nc or not pad[8]:
                    continue
                sd = _pad_signed_dist(pad, x, y)
                if sd < 0.35:
                    hits.append((round(sd, 3), names.get(pad[7]), 'pad'))
            for (ax, ay, bx, by, hw, snc, lay) in obs.segs:
                if snc == nc or lay != 0:
                    continue
                d = _seg_dist(x, y, ax, ay, bx, by) - hw
                if d < 0.35:
                    hits.append((round(d, 3), names.get(snc), 'seg'))
            for (vx, vy, vnc) in getattr(obs, "vias", []):
                if vnc == nc:
                    continue
                import math
                d = math.hypot(x - vx, y - vy) - 0.30
                if d < 0.35:
                    hits.append((round(d, 3), names.get(vnc), 'via'))
            print('blocked at', (round(x, 2), round(y, 2)), sorted(hits)[:3])
            break
