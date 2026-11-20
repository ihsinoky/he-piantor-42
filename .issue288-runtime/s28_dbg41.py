import math, sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, _pad_signed_dist, _seg_dist

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
obs = Obstacles(b)
names = {n.GetNetCode(): n.GetNetname() for n in b.GetNetsByName().values()}
nc = b.FindNet('H_A0_RAW').GetNetCode()
for (x, y) in [(80.3, 121.35), (80.35, 121.15)]:
    print('point', (x, y))
    for pad in obs.pads:
        if pad[7] == nc:
            continue
        sd = _pad_signed_dist(pad, x, y)
        if sd < 0.5:
            print('   pad', names.get(pad[7]), 'sd', round(sd, 3), 'onF', pad[8], 'onB', pad[9])
    for (ax, ay, bx, by, hw, snc, lay) in obs.segs:
        if snc == nc:
            continue
        d = _seg_dist(x, y, ax, ay, bx, by) - hw
        if d < 0.5:
            print('   seg', names.get(snc), 'L', lay, 'sd', round(d, 3))
    for e in obs.vias:
        if e[2] == nc:
            continue
        d = math.hypot(x - e[0], y - e[1]) - 0.30
        if d < 0.5:
            print('   via', names.get(e[2]), 'sd', round(d, 3))
    for e in obs.holes:
        if e[2] == nc:
            continue
        d = math.hypot(x - e[0], y - e[1]) - e[3]
        if d < 0.5:
            print('   hole', names.get(e[2]), 'sd', round(d, 3), 'r', e[3])
