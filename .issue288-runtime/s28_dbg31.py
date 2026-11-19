import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, _seg_clear, _pad_signed_dist, _seg_dist

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
obs = Obstacles(b)
names = {n.GetNetCode(): n.GetNetname() for n in b.GetNetsByName().values()}
def segprobe(net, a, c):
    nc = b.FindNet(net).GetNetCode()
    ok = _seg_clear(obs, a[0], a[1], c[0], c[1], 0, nc, 0.05)
    print(net, a, '->', c, ok)
    if not ok:
        # find first blocked sample
        import math
        steps = max(2, int(math.hypot(c[0] - a[0], c[1] - a[1]) / 0.05))
        for k in range(steps + 1):
            t = k / steps
            x, y = a[0] + (c[0] - a[0]) * t, a[1] + (c[1] - a[1]) * t
            if obs.blocked(x, y, 0, nc, 0.05):
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
                print('  first blocked sample', (round(x, 2), round(y, 2)), sorted(hits)[:3])
                return
pts = [(134.25, 72.3), (134.95, 72.14), (136.5, 72.6), (136.5, 74.3), (134.25, 74.3)]
for a, c in zip(pts, pts[1:]):
    segprobe('H_B3_RAW', a, c)
pts2 = [(117.25, 107.7), (118.05, 108.35), (118.3, 108.6)]
for a, c in zip(pts2, pts2[1:]):
    segprobe('EN_A', a, c)
