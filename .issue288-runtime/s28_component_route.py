"""S2.4b: component-graph repair.

1) Delete MY segments that participate in DRC clearance/shorting errors
   (a segment is 'mine' if no identical segment exists in the donor board,
   modulo the net renames).
2) Build per-net connectivity components from placed pads/tracks/vias and
   repeatedly route the nearest component pair (A*, margin-hardened)
   until every net is one component or no route is found.
DRC (kicad-cli) arbitrates after each outer iteration.
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
import s24_router
from s24_router import Obstacles, add_route, route

s24_router.CLEAR = 0.10  # exact rect model: route at the DRC floor, DRC arbitrates

WT = Path('/home/hatch/workspace/projects/he-piantor-wmatrix')
TREE = WT / 'hardware/kicad/qualification/issue-288-wmatrix'
BOARD = TREE / 'wmatrix.kicad_pcb'
DONOR = WT / 'hardware/kicad/qualification/issue-182-matrix-rev3/board/m1-matrix18.kicad_pcb'
MM = 1e6
POWER_NETS = {'GND', 'HALL_3V3', 'VIN', 'VIN_SRC', 'HALL_3V3_SRC'}
RENAME = {'HALL_5V': 'HALL_3V3', 'MUX_OUT_A': 'MUXA_OUT', 'MUX_OUT_B': 'MUXB_OUT',
          'MUX_OUT_C': 'MUXC_OUT'}
KCLI = '/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr/bin/kicad-cli'
ENV = {'LD_LIBRARY_PATH': '/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr/lib/x86_64-linux-gnu:/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr/lib/kicad',
       'PATH': '/usr/bin:/bin', 'HOME': '/home/hatch'}


def run_drc(tag):
    out = TREE / f'drc-{tag}.json'
    for _ in range(2):
        subprocess.run([KCLI, 'pcb', 'drc', '--output', str(out), '--format', 'json',
                        '--severity-all', str(BOARD)], env=ENV, capture_output=True)
        if out.exists():
            return json.loads(out.read_text())
    raise RuntimeError('drc failed')


def seg_key(net, ax, ay, bx, by, layer, w):
    a = (round(ax, 3), round(ay, 3))
    b = (round(bx, 3), round(by, 3))
    return (net, min(a, b), max(a, b), layer, round(w, 3))


def donor_seg_keys():
    b = pcbnew.LoadBoard(str(DONOR))
    keys = set()
    for t in b.GetTracks():
        if isinstance(t, pcbnew.PCB_VIA):
            continue
        a, e = t.GetStart(), t.GetEnd()
        net = RENAME.get(t.GetNetname(), t.GetNetname())
        keys.add(seg_key(net, a.x / MM, a.y / MM, e.x / MM, e.y / MM,
                         0 if t.GetLayer() == pcbnew.F_Cu else 1, t.GetWidth() / MM))
    return keys


# ---------------------------------------------------------------- components
class Comp:
    """Union-find connectivity over pads/segments/vias of one board state."""

    def __init__(self, board):
        self.items = []   # dicts: kind, net, points...
        self.parent = []
        for fp in board.GetFootprints():
            for pad in fp.Pads():
                if not pad.GetNumber() and pad.GetNetname() == '':
                    continue
                p = pad.GetPosition()
                sz = pad.GetSize()
                layers = pad.GetLayerSet()
                thru = pad.GetDrillSize().x > 0
                self._add({'kind': 'pad', 'net': pad.GetNetname(),
                           'x': p.x / MM, 'y': p.y / MM,
                           'r': max(sz.x, sz.y) / 2 / MM,
                           'layers': (True, True) if thru else
                                     (layers.Contains(pcbnew.F_Cu), layers.Contains(pcbnew.B_Cu))})
        for t in board.GetTracks():
            if isinstance(t, pcbnew.PCB_VIA):
                p = t.GetPosition()
                self._add({'kind': 'via', 'net': t.GetNetname(), 'x': p.x / MM,
                           'y': p.y / MM, 'r': t.GetWidth(pcbnew.F_Cu) / 2 / MM,
                           'layers': (True, True)})
            else:
                a, e = t.GetStart(), t.GetEnd()
                self._add({'kind': 'seg', 'net': t.GetNetname(),
                           'ax': a.x / MM, 'ay': a.y / MM, 'bx': e.x / MM, 'by': e.y / MM,
                           'w': t.GetWidth() / MM,
                           'layers': (t.GetLayer() == pcbnew.F_Cu, t.GetLayer() == pcbnew.B_Cu)})
        self._union_all()

    def _add(self, it):
        self.items.append(it)
        self.parent.append(len(self.items) - 1)

    def find(self, i):
        while self.parent[i] != i:
            self.parent[i] = self.parent[self.parent[i]]
            i = self.parent[i]
        return i

    def union(self, i, j):
        a, b = self.find(i), self.find(j)
        if a != b:
            self.parent[a] = b

    @staticmethod
    def _pts(it):
        if it['kind'] == 'seg':
            return [(it['ax'], it['ay']), (it['bx'], it['by'])]
        return [(it['x'], it['y'])]

    def _touch(self, a, b):
        if a['net'] != b['net'] or a['net'] == '':
            return False
        shared_layer = (a['layers'][0] and b['layers'][0]) or (a['layers'][1] and b['layers'][1])
        if not shared_layer:
            return False
        for (ax, ay) in self._pts(a):
            for (bx, by) in self._pts(b):
                if math.hypot(ax - bx, ay - by) <= 0.02:
                    return True
            if b['kind'] == 'seg':
                if self._pt_seg(ax, ay, b) <= (a.get('r', 0) if a['kind'] != 'seg' else a['w'] / 2) + b['w'] / 2 + 0.02:
                    return True
            if b['kind'] in ('pad', 'via') and math.hypot(ax - b['x'], ay - b['y']) <= b['r'] + 0.02:
                return True
        if a['kind'] == 'seg' and b['kind'] == 'seg':
            # crossing segments on the same layer
            if self._seg_seg(a, b):
                return True
        return False

    @staticmethod
    def _pt_seg(px, py, s):
        dx, dy = s['bx'] - s['ax'], s['by'] - s['ay']
        L2 = dx * dx + dy * dy
        if L2 == 0:
            return math.hypot(px - s['ax'], py - s['ay'])
        t = max(0.0, min(1.0, ((px - s['ax']) * dx + (py - s['ay']) * dy) / L2))
        return math.hypot(px - (s['ax'] + t * dx), py - (s['ay'] + t * dy))

    @staticmethod
    def _seg_seg(a, b):
        def orient(px, py, qx, qy, rx, ry):
            v = (qx - px) * (ry - py) - (qy - py) * (rx - px)
            return 0 if abs(v) < 1e-9 else (1 if v > 0 else -1)
        d1 = orient(b['ax'], b['ay'], b['bx'], b['by'], a['ax'], a['ay'])
        d2 = orient(b['ax'], b['ay'], b['bx'], b['by'], a['bx'], a['by'])
        d3 = orient(a['ax'], a['ay'], a['bx'], a['by'], b['ax'], b['ay'])
        d4 = orient(a['ax'], a['ay'], a['bx'], a['by'], b['bx'], b['by'])
        return d1 * d2 < 0 and d3 * d4 < 0

    def _union_all(self):
        # spatial hash on item anchor points, 2mm cells
        grid = {}
        for i, it in enumerate(self.items):
            for (x, y) in self._pts(it):
                grid.setdefault((int(x // 2), int(y // 2)), []).append(i)
        cand = set()
        for i, it in enumerate(self.items):
            for (x, y) in self._pts(it):
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        for j in grid.get((int(x // 2) + dx, int(y // 2) + dy), []):
                            if j > i:
                                cand.add((i, j))
            # long segments can span cells: also register midpoint
        for (i, j) in cand:
            if self.find(i) != self.find(j) and self._touch(self.items[i], self.items[j]):
                self.union(i, j)

    def components(self, net):
        comps = {}
        for i, it in enumerate(self.items):
            if it['net'] == net:
                comps.setdefault(self.find(i), []).append(i)
        return list(comps.values())

    def nearest_pair(self, comp_a, comp_b):
        """Closest (point_on_a, layer_a, point_on_b, layer_b) between components."""
        best = None
        for i in comp_a:
            a = self.items[i]
            for j in comp_b:
                b = self.items[j]
                for (ax, ay) in self._pts(a):
                    cands = [(ax, ay, bx, by) for (bx, by) in self._pts(b)]
                    if b['kind'] == 'seg':
                        # projection of a-point onto b segment
                        dx, dy = b['bx'] - b['ax'], b['by'] - b['ay']
                        L2 = dx * dx + dy * dy
                        if L2 > 0:
                            t = max(0.0, min(1.0, ((ax - b['ax']) * dx + (ay - b['ay']) * dy) / L2))
                            cands.append((ax, ay, b['ax'] + t * dx, b['ay'] + t * dy))
                    for (px, py, qx, qy) in cands:
                        d = math.hypot(px - qx, py - qy)
                        if best is None or d < best[0]:
                            la = 0 if a['layers'][0] else 1
                            lb = 0 if b['layers'][0] else 1
                            # prefer F layer when the item spans both
                            if a['kind'] in ('pad', 'via'):
                                la = 0
                            if b['kind'] in ('pad', 'via'):
                                lb = 0
                            best = (d, (px, py, la), (qx, qy, lb))
        return best


# ---------------------------------------------------------------- step 1
def delete_my_bad_segments():
    d = run_drc('hard')
    bad = []
    for v in d['violations']:
        if v.get('severity') == 'error' and v['type'] in ('clearance', 'shorting_items',
                                                          'solder_mask_bridge', 'hole_clearance'):
            for it in v['items']:
                if it.get('description', '').startswith('Track'):
                    bad.append(it)
    if not bad:
        print('step1: no error tracks to delete')
        return
    keys = donor_seg_keys()
    b = pcbnew.LoadBoard(str(BOARD))
    fps = list(b.GetFootprints())  # snapshot before mutation (swig quirk)
    tracks = list(b.GetTracks())
    killed = 0
    for t in tracks:
        if isinstance(t, pcbnew.PCB_VIA):
            continue
        a, e = t.GetStart(), t.GetEnd()
        k = seg_key(t.GetNetname(), a.x / MM, a.y / MM, e.x / MM, e.y / MM,
                    0 if t.GetLayer() == pcbnew.F_Cu else 1, t.GetWidth() / MM)
        if k not in keys:
            # is this segment one of the error items? match by net + proximity to item pos
            for it in bad:
                import re
                m = re.search(r'\[([^\]]+)\]', it.get('description', ''))
                if m and m.group(1) == t.GetNetname():
                    p = it['pos']
                    if min(math.hypot(a.x / MM - p['x'], a.y / MM - p['y']),
                           math.hypot(e.x / MM - p['x'], e.y / MM - p['y'])) < 3.0:
                        b.Remove(t)
                        killed += 1
                        break
    b.Save(str(BOARD))
    print(f'step1: deleted {killed} of my segments in error pairs')


# ---------------------------------------------------------------- step 2
def connect_components(max_outer=10):
    for outer in range(max_outer):
        b = pcbnew.LoadBoard(str(BOARD))
        comp = Comp(b)
        obs = Obstacles(b)
        nets = sorted({it['net'] for it in comp.items if it['net']})
        total_split = 0
        routed = failed = 0
        for net in nets:
            comps = comp.components(net)
            if len(comps) <= 1:
                continue
            total_split += len(comps) - 1
            # greedy chaining: connect nearest pair until one component
            work = [list(c) for c in comps]
            guard = 0
            while len(work) > 1 and guard < 12:
                guard += 1
                best = None
                for ii in range(len(work)):
                    for jj in range(ii + 1, len(work)):
                        r = comp.nearest_pair(work[ii], work[jj])
                        if r and (best is None or r[0] < best[0][0]):
                            best = (r, ii, jj)
                if best is None:
                    break
                (dist, pa, pb), ii, jj = best
                netobj = b.FindNet(net)
                width = 0.30 if net in POWER_NETS else 0.10
                res = route(obs, pa, pb, netobj.GetNetCode(), width)
                if res is None:
                    failed += 1
                    # mark pair as unconnectable this round by merging artificially
                    work[ii] = work[ii] + work[jj]
                    del work[jj]
                    continue
                points, vias = res
                add_route(b, netobj, width, points, vias)
                for (ax, ay, al), (bx, by, bl) in zip(points, points[1:]):
                    if al == bl:
                        obs.add_seg(ax, ay, bx, by, width / 2, netobj.GetNetCode(), al)
                for (vx, vy) in vias:
                    obs.add_via(vx, vy, 0.30, netobj.GetNetCode())
                work[ii] = work[ii] + work[jj]
                del work[jj]
                routed += 1
        b.Save(str(BOARD))
        d = run_drc(f'c{outer}')
        errs = [v for v in d['violations'] if v.get('severity') == 'error']
        print(f'outer {outer}: split-nets pending {total_split}, routed {routed}, '
              f'failed {failed} | DRC unconnected {len(d["unconnected_items"])}, errors {len(errs)}', flush=True)
        if len(d['unconnected_items']) == 0:
            break


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'step1':
        delete_my_bad_segments()
    else:
        connect_components()
