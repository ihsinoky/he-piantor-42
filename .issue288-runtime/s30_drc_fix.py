"""S2.4e DRC-driven pair fixer.

Loop: run kicad-cli DRC (severity-all, JSON) -> take the first
unconnected pair -> resolve both items to board anchors (pad centre /
via centre / closest point on the named track) -> route() between the
anchors (0.25 grid, then 0.125 grid) -> save -> repeat.
Errors: delete my segments participating in error pairs first
(s28 step1 logic), the loop then re-routes the fallout.
Stops when DRC shows 0 unconnected + 0 errors, or a pair fails twice.
"""
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
import s24_router
from s24_router import Obstacles, add_route, route
from s28_component_route import POWER_NETS, donor_seg_keys, seg_key

WT = Path('/home/hatch/workspace/projects/he-piantor-wmatrix')
TREE = WT / 'hardware/kicad/qualification/issue-288-wmatrix'
BOARD = TREE / 'wmatrix.kicad_pcb'
RT = WT / '.issue288-runtime'
MM = 1e6
KCLI = '/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr/bin/kicad-cli'
ENV = dict(os.environ)


def run_drc(tag):
    out = RT / f'drc-{tag}.json'
    subprocess.run([KCLI, 'pcb', 'drc', '--output', str(out), '--format', 'json',
                    '--severity-all', str(BOARD)], capture_output=True, env=ENV, check=True)
    return json.loads(out.read_text())


def anchors(b, item):
    """Resolve a DRC item to (net, [(x, y, layer), ...]) anchor candidates."""
    desc = item.get('description', '')
    pos = item['pos']
    x, y = pos['x'], pos['y']
    if desc.startswith('Pad'):
        # Pad N [NET] of REF ...
        num = desc.split()[1]
        ref = desc.split(' of ')[1].split(' on ')[0]
        fp = next(f for f in b.GetFootprints() if f.GetReference() == ref)
        pad = next(p for p in fp.Pads() if p.GetNumber() == num)
        pp = pad.GetPosition()
        layers = [0] if not pad.IsOnLayer(pcbnew.B_Cu) else [0, 1]
        return pad.GetNetname(), [(pp.x / MM, pp.y / MM, l) for l in layers]
    if desc.startswith('Via'):
        net = desc.split('[')[1].split(']')[0]
        return net, [(x, y, 0), (x, y, 1)]
    if desc.startswith('Track'):
        net = desc.split('[')[1].split(']')[0]
        layer = 0 if 'F.Cu' in desc else 1
        # find the track whose start matches pos (DRC pos = start point)
        best = None
        for t in b.GetTracks():
            if t.Type() != pcbnew.PCB_TRACE_T or t.GetNetname() != net:
                continue
            if (t.GetLayer() == pcbnew.F_Cu) != (layer == 0):
                continue
            s = t.GetStart()
            d = math.hypot(s.x / MM - x, s.y / MM - y)
            if best is None or d < best[0]:
                best = (d, t)
        t = best[1]
        s, e = t.GetStart(), t.GetEnd()
        return net, [(s.x / MM, s.y / MM, layer), (e.x / MM, e.y / MM, layer)]
    return None, []


def closest_pair(aa, bb):
    best = None
    for a in aa:
        for c in bb:
            d = math.hypot(a[0] - c[0], a[1] - c[1])
            if best is None or d < best[0]:
                best = (d, a, c)
    return best


def main():
    failed = {}
    max_it = 1 if '--once' in sys.argv else 40
    for it in range(max_it):
        d = run_drc(f'fix{it}')
        errs = [v for v in d['violations'] if v.get('severity') == 'error']
        unc = d['unconnected_items']
        print(f'iter {it}: errors {len(errs)} unconnected {len(unc)}', flush=True)
        if not errs and not unc:
            print('CONVERGED: 0 errors / 0 unconnected')
            return
        b = pcbnew.LoadBoard(str(BOARD))
        if errs:
            # delete my (non-donor) segments participating in error pairs
            keys = donor_seg_keys()
            pts = [(v, i) for v in errs for i in v['items']]
            n = 0
            for t in list(b.GetTracks()):
                if t.Type() != pcbnew.PCB_TRACE_T:
                    continue
                s, e = t.GetStart(), t.GetEnd()
                k = seg_key(t.GetNetname(), s.x / MM, s.y / MM, e.x / MM, e.y / MM,
                            0 if t.GetLayer() == pcbnew.F_Cu else 1, t.GetWidth() / MM)
                if k in keys:
                    continue
                for _v, it in pts:
                    if '[' + t.GetNetname() + ']' in it.get('description', ''):
                        p = it['pos']
                        if min(math.hypot(s.x / MM - p['x'], s.y / MM - p['y']),
                               math.hypot(e.x / MM - p['x'], e.y / MM - p['y'])) < 3.0:
                            b.Remove(t)
                            n += 1
                            break
            print(f'  deleted {n} my segments in error pairs', flush=True)
            b.Save(str(BOARD))
            continue
        # fix the first unconnected pair not in the skip file
        skipf = RT / 'drcfix-skip.txt'
        skips = set(skipf.read_text().splitlines()) if skipf.exists() else set()
        u = None
        for cand in unc:
            k = (cand['items'][0].get('description', '')[:40],
                 cand['items'][1].get('description', '')[:40])
            if '|'.join(k) not in skips:
                u = cand
                break
        if u is None:
            print('all remaining pairs are skipped - stopping')
            return
        ia, ib = u['items'][0], u['items'][1]
        key = (ia.get('description', '')[:40], ib.get('description', '')[:40])
        if failed.get(key, 0) >= 2:
            print('  pair failed twice, stopping:', key)
            return
        na, aa = anchors(b, ia)
        nb, ab = anchors(b, ib)
        net = na or nb
        if not aa or not ab:
            print('  cannot resolve anchors:', key)
            failed[key] = 9
            continue
        _, pa, pb = closest_pair(aa, ab)
        obs = Obstacles(b)
        netobj = b.FindNet(net)
        width = 0.30 if net in POWER_NETS else 0.10
        res = route(obs, pa, pb, netobj.GetNetCode(), width)
        if not res:
            s24_router.GRID = 0.125
            try:
                res = route(obs, pa, pb, netobj.GetNetCode(), width)
            finally:
                s24_router.GRID = 0.25
        if res:
            add_route(b, netobj, width, res[0], res[1])
            b.Save(str(BOARD))
            print(f'  routed {net}: {key[0]} <-> {key[1]}', flush=True)
        else:
            failed[key] = failed.get(key, 0) + 1
            with open(RT / 'drcfix-skip.txt', 'a') as fh:
                fh.write('|'.join(key) + '\n')
            print(f'  ROUTE FAILED {net}: {key} (skipped henceforth)', flush=True)


if __name__ == '__main__':
    main()
