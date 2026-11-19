import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, _seg_clear, _pad_signed_dist, _seg_dist

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
obs = Obstacles(b)
names = {n.GetNetCode(): n.GetNetname() for n in b.GetNetsByName().values()}
def probe(net, x, y, via=False):
    nc = b.FindNet(net).GetNetCode()
    hits = []
    for pad in obs.pads:
        if pad[7] == nc:
            continue
        sd = _pad_signed_dist(pad, x, y)
        if sd < 0.6:
            hits.append((round(sd, 3), names.get(pad[7]), 'pad'))
    for (ax, ay, bx, by, hw, snc, lay) in obs.segs:
        if snc == nc:
            continue
        d = _seg_dist(x, y, ax, ay, bx, by) - hw
        if d < 0.6:
            hits.append((round(d, 3), names.get(snc), f'segL{lay}'))
    print((x, y), 'via' if via else '', sorted(hits)[:4])
nc = b.FindNet('H_A5_RAW').GetNetCode()
print('arc seg1:', _seg_clear(obs, 117.25, 106.3, 118.75, 106.3, 0, nc, 0.05))
print('arc seg2:', _seg_clear(obs, 118.75, 106.3, 118.75, 109.5, 0, nc, 0.05))
probe('H_A5_RAW', 118.75, 108.0)
probe('EN_C', 150.9, 90.9, via=True)
probe('EN_C', 151.07, 90.8)
