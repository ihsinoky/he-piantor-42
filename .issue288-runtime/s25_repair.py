"""S2.4 repair driver: window clear -> DRC-driven A* repair -> dangling prune.

Usage: runpy.sh s25_repair.py [clear|route|prune|all]
State lives in the saved board file; DRC JSON is produced by kicad-cli
between rounds (see s25_drc.sh).
"""
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, add_route, route

WT = Path('/home/hatch/workspace/projects/he-piantor-wmatrix')
TREE = WT / 'hardware/kicad/qualification/issue-288-wmatrix'
BOARD = TREE / 'wmatrix.kicad_pcb'
MM = 1e6
POWER_NETS = {'GND', 'HALL_3V3', 'VIN', 'VIN_SRC', 'HALL_3V3_SRC'}


def load():
    return pcbnew.LoadBoard(str(BOARD))


def run_drc(tag):
    env = {'LD_LIBRARY_PATH': '/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr/lib/x86_64-linux-gnu:/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr/lib/kicad',
           'PATH': '/usr/bin:/bin', 'HOME': '/home/hatch'}
    out = TREE / f'drc-{tag}.json'
    for attempt in range(2):
        r = subprocess.run(['/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr/bin/kicad-cli',
                            'pcb', 'drc', '--output', str(out), '--format', 'json', '--severity-all',
                            str(BOARD)], env=env, capture_output=True)
        if out.exists():
            return json.loads(out.read_text())
        print(f'  DRC attempt {attempt} produced no file: rc={r.returncode} err={r.stderr.decode()[:200]}', flush=True)
    raise RuntimeError(f'DRC failed for {tag}')


# ------------------------------------------------------------------- clear
def do_clear():
    b = load()
    fps = list(b.GetFootprints())
    tracks = list(b.GetTracks())
    centres = []
    for fp in fps:
        if fp.GetReference().startswith('U_H'):
            p = fp.GetPosition()
            centres.append((p.x / MM, p.y / MM))
    killed = 0
    for t in tracks:
        if isinstance(t, pcbnew.PCB_VIA):
            p = t.GetPosition()
            pts = [(p.x / MM, p.y / MM)]
        else:
            a, e = t.GetStart(), t.GetEnd()
            pts = [(a.x / MM, a.y / MM), (e.x / MM, e.y / MM)]
        for (cx, cy) in centres:
            if any(abs(x - cx) <= 3.2 and abs(y - cy) <= 3.2 for (x, y) in pts):
                b.Remove(t)
                killed += 1
                break
    b.Save(str(BOARD))
    print(f'clear: removed {killed} tracks/vias in sensor windows')


# ------------------------------------------------------------------- route
NET_RE = re.compile(r'\[([^\]]+)\]')


def parse_unc(item):
    """DRC unconnected item -> list of (net, x, y, layer)."""
    out = []
    for it in item['items']:
        desc = it.get('description', '')
        m = NET_RE.search(desc)
        net = m.group(1) if m else None
        layer = 1 if 'B.Cu' in desc else 0
        out.append((net, it['pos']['x'], it['pos']['y'], layer))
    return out


def do_route(rounds=14):
    for rnd in range(rounds):
        d = run_drc(f'r{rnd}')
        unc = d['unconnected_items']
        errs = [v for v in d['violations'] if v.get('severity') == 'error']
        print(f'round {rnd}: unconnected {len(unc)}, error violations {len(errs)}', flush=True)
        if not unc:
            break
        b = load()
        obs = Obstacles(b)
        used_endpoints = set()
        routed = failed = 0
        for item in unc:
            pair = parse_unc(item)
            if len(pair) != 2 or pair[0][0] is None:
                continue
            (n1, x1, y1, l1), (n2, x2, y2, l2) = pair
            if n1 != n2:
                continue
            key = (round(x1, 1), round(y1, 1))
            key2 = (round(x2, 1), round(y2, 1))
            if key in used_endpoints or key2 in used_endpoints:
                continue
            net = b.FindNet(n1)
            width = 0.30 if n1 in POWER_NETS else 0.10
            res = route(obs, (x1, y1, l1), (x2, y2, l2), net.GetNetCode(), width)
            if res is None:
                failed += 1
                continue
            points, vias = res
            add_route(b, net, width, points, vias)
            # register the new copper as obstacles for other nets
            for (ax, ay, al), (bx, by, bl) in zip(points, points[1:]):
                if al == bl:
                    obs.segs.append((ax, ay, bx, by, width / 2, net.GetNetCode(), al))
            for (vx, vy) in vias:
                obs.vias.append((vx, vy, 0.30, net.GetNetCode()))
            used_endpoints.add(key)
            used_endpoints.add(key2)
            routed += 1
        b.Save(str(BOARD))
        print(f'  routed {routed}, failed {failed}', flush=True)
        if routed == 0:
            break


# ------------------------------------------------------------------- prune
def do_prune():
    for it in range(30):
        b = load()
        fps = list(b.GetFootprints())
        tracks = list(b.GetTracks())
        pads = []
        for fp in fps:
            for pad in fp.Pads():
                p = pad.GetPosition()
                sz = pad.GetSize()
                pads.append((p.x / MM, p.y / MM, max(sz.x, sz.y) / 2 / MM,
                             pad.GetNetCode(), pad.GetLayerSet().Contains(pcbnew.F_Cu),
                             pad.GetLayerSet().Contains(pcbnew.B_Cu)))
        segs = []
        vias = []
        for t in tracks:
            if isinstance(t, pcbnew.PCB_VIA):
                p = t.GetPosition()
                vias.append((t, p.x / MM, p.y / MM, t.GetNetCode()))
            else:
                a, e = t.GetStart(), t.GetEnd()
                segs.append((t, a.x / MM, a.y / MM, e.x / MM, e.y / MM,
                             t.GetWidth() / MM, t.GetNetCode(),
                             0 if t.GetLayer() == pcbnew.F_Cu else 1))

        def endpoint_free(x, y, layer, netcode, skip):
            for (px, py, r, nc, on_f, on_b) in pads:
                if nc != netcode:
                    continue
                if layer == 0 and not on_f:
                    continue
                if layer == 1 and not on_b:
                    continue
                if math.hypot(x - px, y - py) <= r + 0.02:
                    return False
            for (vt, vx, vy, nc) in vias:
                if nc == netcode and math.hypot(x - vx, y - vy) <= 0.05:
                    return False
            for (st, ax, ay, bx, by, w, nc, lay) in segs:
                if st is skip or nc != netcode or lay != layer:
                    continue
                if math.hypot(x - ax, y - ay) <= 0.02 or math.hypot(x - bx, y - by) <= 0.02:
                    return False
                # endpoint lying on the segment body
                dx, dy = bx - ax, by - ay
                L2 = dx * dx + dy * dy
                if L2 > 0:
                    tt = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / L2))
                    if math.hypot(x - (ax + tt * dx), y - (ay + tt * dy)) <= w / 2 + 0.02:
                        return False
            return True

        removed = 0
        for (t, ax, ay, bx, by, w, nc, lay) in segs:
            if endpoint_free(ax, ay, lay, nc, t) or endpoint_free(bx, by, lay, nc, t):
                b.Remove(t)
                removed += 1
        # vias with nothing attached on either layer
        for (vt, vx, vy, nc) in vias:
            deg = 0
            for (px, py, r, pnc, on_f, on_b) in pads:
                if pnc == nc and math.hypot(vx - px, vy - py) <= r + 0.02:
                    deg += 1
            for (st, ax, ay, bx, by, w, snc, lay) in segs:
                if snc != nc:
                    continue
                if math.hypot(vx - ax, vy - ay) <= 0.05 or math.hypot(vx - bx, vy - by) <= 0.05:
                    deg += 1
            if deg == 0:
                b.Remove(vt)
                removed += 1
        b.Save(str(BOARD))
        print(f'prune pass {it}: removed {removed}')
        if removed == 0:
            break


if __name__ == '__main__':
    what = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if what in ('clear', 'all'):
        do_clear()
    if what in ('route', 'all'):
        do_route()
    if what in ('prune', 'all'):
        do_prune()
