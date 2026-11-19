"""S2.4h last-mile: HA5 EN re-route, MUXA_OUT remnant, HB3 OUT + HC5 EN cages."""
import math
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, add_route, route, _seg_clear
from s28_component_route import Comp
from s29_finish import escape_pad, try_connect

WT = Path('/home/hatch/workspace/projects/he-piantor-wmatrix')
TREE = WT / 'hardware/kicad/qualification/issue-288-wmatrix'
BOARD = TREE / 'wmatrix.kicad_pcb'
MM = 1e6
step = sys.argv[1]
b = pcbnew.LoadBoard(str(BOARD))

if step == 'del':
    n = 0
    for t in list(b.GetTracks()):
        if t.Type() != pcbnew.PCB_TRACE_T:
            continue
        s = t.GetStart()
        # EN_A first segment grazing HA5 GND pad
        if t.GetNetname() == 'EN_A' and math.hypot(s.x / MM - 117.119643, s.y / MM - 107.819643) < 0.3:
            b.Remove(t); n += 1
        # MUXA_OUT remnant starting at (78.45,124.05)
        if t.GetNetname() == 'MUXA_OUT' and math.hypot(s.x / MM - 78.45, s.y / MM - 124.05) < 0.3:
            b.Remove(t); n += 1
    b.Save(str(BOARD))
    print('deleted', n)

elif step == 'ha5':
    netobj = b.FindNet('EN_A')
    nc = netobj.GetNetCode()
    obs = Obstacles(b)
    ok = _seg_clear(obs, 117.25, 107.7, 117.25, 108.7, 0, nc, 0.05)
    print('HA5 south stub clear:', ok)
    if ok:
        add_route(b, netobj, 0.10, [(117.25, 107.7, 0), (117.25, 108.7, 0)], [])
        b.Save(str(BOARD))
        b = pcbnew.LoadBoard(str(BOARD))
        obs = Obstacles(b)
        res = route(obs, (117.25, 108.7, 0), (115.869643, 104.319643, 0), nc, 0.10)
        print('HA5 stub->via route:', bool(res))
        if res:
            add_route(b, netobj, 0.10, res[0], res[1])
            b.Save(str(BOARD))

elif step == 'cages':
    # HB3 OUT pad + HC5 EN pad: delete window-local RAW cage, escape/route, reconnect
    jobs = [('U_HB3', 'H_B3_RAW', 'out'), ('U_HC5', 'H_C5_RAW', 'en')]
    for ref, raw_net, kind in jobs:
        b = pcbnew.LoadBoard(str(BOARD))
        fp = next(f for f in list(b.GetFootprints()) if f.GetReference() == ref)
        p = fp.GetPosition()
        cx, cy = p.x / MM, p.y / MM
        doomed = []
        for t in list(b.GetTracks()):
            if t.Type() != pcbnew.PCB_TRACE_T or t.GetNetname() != raw_net:
                continue
            s, e = t.GetStart(), t.GetEnd()
            if all(abs(q.x / MM - cx) <= 3.2 and abs(q.y / MM - cy) <= 3.2 for q in (s, e)):
                doomed.append(t)
        for t in doomed:
            b.Remove(t)
        print(f'{ref}: deleted {len(doomed)} cage segs of {raw_net}')
        b.Save(str(BOARD))
        b = pcbnew.LoadBoard(str(BOARD))
        obs = Obstacles(b)
        comp = Comp(b)
        if kind == 'out':
            netobj = b.FindNet(raw_net)
            # OUT pad at local (+0.25,-0.70)
            res = route(obs, (cx + 0.25, cy - 0.7, 0), (130.5, 73.0, 0) if ref == 'U_HB3' else (cx, cy, 0),
                        netobj.GetNetCode(), 0.10)
            print(f'{ref} OUT route:', bool(res))
            if res:
                add_route(b, netobj, 0.10, res[0], res[1])
                b.Save(str(BOARD))
        else:
            en_net = 'EN_C'
            pad_item = None
            for c in comp.components(en_net):
                if len(c) == 1 and comp.items[c[0]]['kind'] == 'pad':
                    it = comp.items[c[0]]
                    if abs(it['x'] - (cx + 0.25)) < 0.3 and abs(it['y'] - (cy + 0.7)) < 0.3:
                        pad_item = it
            if pad_item is not None:
                ok = escape_pad(b, obs, en_net, pad_item)
                print(f'{ref} EN escape:', ok)
                b.Save(str(BOARD))
                b = pcbnew.LoadBoard(str(BOARD))
                obs = Obstacles(b)
                comp = Comp(b)
                comps = comp.components(en_net)
                if len(comps) > 1:
                    try_connect(b, obs, comp, en_net, comps)
                    b.Save(str(BOARD))
            # reconnect the RAW net split by the cage deletion
            b = pcbnew.LoadBoard(str(BOARD))
            obs = Obstacles(b)
            comp = Comp(b)
            comps = comp.components(raw_net)
            if len(comps) > 1:
                if try_connect(b, obs, comp, raw_net, comps):
                    b.Save(str(BOARD))
            print(f'{ref} done')
