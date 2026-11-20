import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
import s24_router
from s24_router import Obstacles, route
from s28_component_route import Comp, POWER_NETS

s24_router.CLEAR = 0.10  # exact rect model: route at the DRC floor, DRC arbitrates
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
comp = Comp(b)
obs = Obstacles(b)
for net in sorted({it['net'] for it in comp.items if it['net']}):
    comps = comp.components(net)
    if len(comps) <= 1:
        continue
    sizes = [len(c) for c in comps]
    # nearest pair
    best = None
    for ii in range(len(comps)):
        for jj in range(ii + 1, len(comps)):
            r = comp.nearest_pair(comps[ii], comps[jj])
            if r and (best is None or r[0] < best[0]):
                best = r
    dist, pa, pb = best
    netobj = b.FindNet(net)
    width = 0.30 if net in POWER_NETS else 0.10
    res = route(obs, pa, pb, netobj.GetNetCode(), width)
    print(f'{net}: {len(comps)} comps sizes={sizes} nearest={dist:.2f}mm {pa} -> {pb} route={"OK" if res else "FAIL"}')
