"""S2.4d EN cage fix.

For each sensor whose EN pad is a singleton component: delete my routed
segments of that sensor's RAW net lying fully inside the sensor's
+-3.2mm window (the cage the S2.4 router wrapped around the EN pad),
place the scripted EN escape, then reconnect RAW and EN with the
component router. DRC arbitrates afterwards.
"""
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles
from s28_component_route import Comp
from s29_finish import escape_pad, try_connect

WT = Path('/home/hatch/workspace/projects/he-piantor-wmatrix')
TREE = WT / 'hardware/kicad/qualification/issue-288-wmatrix'
BOARD = TREE / 'wmatrix.kicad_pcb'
MM = 1e6


def main():
    b = pcbnew.LoadBoard(str(BOARD))
    comp = Comp(b)
    # sensor centres from footprint positions
    sensors = {}
    for f in list(b.GetFootprints()):
        ref = f.GetReference()
        if ref.startswith('U_H') and len(ref) == 5:
            p = f.GetPosition()
            sensors[ref] = (p.x / MM, p.y / MM)
    targets = []
    for ref, (cx, cy) in sensors.items():
        g, i = ref[3], ref[4]
        en_net = f'EN_{g}'
        comps = comp.components(en_net)
        for c in comps:
            if len(c) == 1 and comp.items[c[0]]['kind'] == 'pad':
                it = comp.items[c[0]]
                if abs(it['x'] - (cx + 0.25)) < 0.3 and abs(it['y'] - (cy + 0.7)) < 0.3:
                    targets.append((ref, g, i, it))
    print('caged EN pads:', [(t[0], round(t[3]['x'], 2), round(t[3]['y'], 2)) for t in targets])
    obs = Obstacles(b)
    for ref, g, i, pad_item in targets:
        cx, cy = sensors[ref]
        raw_net = f'H_{g}{i}_RAW'
        # delete window-local RAW segments (snapshot first)
        doomed = []
        for t in list(b.GetTracks()):
            if t.Type() != pcbnew.PCB_TRACE_T or t.GetNetname() != raw_net:
                continue
            s, e = t.GetStart(), t.GetEnd()
            pts = [(s.x / MM, s.y / MM), (e.x / MM, e.y / MM)]
            if all(abs(x - cx) <= 3.2 and abs(y - cy) <= 3.2 for x, y in pts):
                doomed.append(t)
        for t in doomed:
            b.Remove(t)
        print(f'{ref}: deleted {len(doomed)} cage segments of {raw_net}')
        obs = Obstacles(b)
        ok = escape_pad(b, obs, f'EN_{g}', pad_item)
        print(f'{ref}: escape {"OK" if ok else "FAILED"}')
        obs = Obstacles(b)
        comp = Comp(b)
        for net in (raw_net, f'EN_{g}'):
            comps = comp.components(net)
            if len(comps) > 1:
                if try_connect(b, obs, comp, net, comps):
                    comp = Comp(b)
                    obs = Obstacles(b)
    b.Save(str(BOARD))
    print('saved')


if __name__ == '__main__':
    main()
