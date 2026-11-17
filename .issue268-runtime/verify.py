"""Issue #268 stage 4 verification battery:
1) J_WING / J2 / J3 pad->net tables: Matrix Rev.4, Wing Rev.5 17L/17R, Main Rev.8 vs D-024.
2) Outline (Edge.Cuts) equality Rev.3 vs Rev.4.
3) Footprint census diff Rev.3 vs Rev.4 (only J_WING may differ).
4) Copper diff per net Rev.3 -> Rev.4 + change bbox.
5) Via-pad audit (annulus edge to pad edge, all pads, same-net not exempt) Rev.4 + Rev.3.
Outputs verify4.json + printed summary."""
import json, math
import pcbnew as p

mm = lambda v: v / 1e6
REV4 = 'hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb'
REV3 = '/home/hatch/workspace/projects/he-piantor-42/hardware/kicad/qualification/issue-182-matrix-rev3/board/m1-matrix18.kicad_pcb'
W17L = '/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation/wing-rev5-17mm-left/main.kicad_pcb'
W17R = '/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation/wing-rev5-17mm-right/main.kicad_pcb'
MAIN8 = '/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation/main-rev8/main.kicad_pcb'
D024 = {1: 'HALL_5V', 2: 'GND', 3: 'MUX_A0', 4: 'GND', 5: 'MUX_A1', 6: 'MUX_A2', 7: 'WING_EN',
        8: 'GND', 9: 'MUX_OUT_A', 10: 'GND', 11: 'MUX_OUT_B', 12: 'GND', 13: 'MUX_OUT_C', 14: 'GND'}
out = {}

def jwing_table(path, ref='J_WING'):
    b = p.LoadBoard(path)
    for fp in b.GetFootprints():
        if fp.GetReference() != ref:
            continue
        t = {}
        for pad in fp.Pads():
            n = pad.GetNumber()
            if n.isdigit():
                t[int(n)] = pad.GetNetname()
        return t
    return {}

def check(name, table, expect):
    ok = all(table.get(n) == expect(n) for n in range(1, 15))
    out[name] = {'table': {str(k): table.get(k) for k in range(1, 15)}, 'pass': ok}
    print(name, 'PASS' if ok else 'FAIL', [table.get(n) for n in range(1, 15)])

check('matrix_rev4_J_WING', jwing_table(REV4), lambda n: D024[n])
check('wing17L_J_WING', jwing_table(W17L), lambda n: D024[n])
check('wing17R_J_WING', jwing_table(W17R), lambda n: D024[n])
check('main8_J2', jwing_table(MAIN8, 'J2'), lambda n: D024[15 - n])
check('main8_J3', jwing_table(MAIN8, 'J3'), lambda n: D024[15 - n])

b3, b4 = p.LoadBoard(REV3), p.LoadBoard(REV4)

def outline(b):
    segs = []
    for d in b.GetDrawings():
        if d.GetLayerName() != 'Edge.Cuts':
            continue
        s, e = d.GetStart(), d.GetEnd()
        segs.append((round(mm(s.x), 3), round(mm(s.y), 3), round(mm(e.x), 3), round(mm(e.y), 3)))
    return sorted(segs)
o3, o4 = outline(b3), outline(b4)
out['outline_equal'] = (o3 == o4)
print('outline segments rev3/rev4:', len(o3), len(o4), 'equal:', o3 == o4)

def census(b):
    c = {}
    for fp in b.GetFootprints():
        pos = fp.GetPosition()
        c[fp.GetReference()] = (round(mm(pos.x), 3), round(mm(pos.y), 3),
                                round(fp.GetOrientationDegrees(), 1), fp.GetLayerName(),
                                fp.GetFPID().GetLibItemName())
    return c
c3, c4 = census(b3), census(b4)
diffs = {r: (c3.get(r), c4.get(r)) for r in set(c3) | set(c4) if c3.get(r) != c4.get(r)}
out['footprint_count'] = (len(c3), len(c4))
out['footprint_diffs'] = {r: [str(a), str(bb)] for r, (a, bb) in diffs.items()}
print('footprints rev3/rev4:', len(c3), len(c4), 'diffs:', list(diffs))

def copper(b):
    from collections import Counter
    c = Counter()
    for t in b.GetTracks():
        s, e = t.GetStart(), t.GetEnd()
        if isinstance(t, p.PCB_VIA):
            c[(t.GetNetname(), 'VIA', round(mm(s.x), 2), round(mm(s.y), 2))] += 1
        else:
            c[(t.GetNetname(), t.GetLayerName(), round(mm(s.x), 2), round(mm(s.y), 2),
               round(mm(e.x), 2), round(mm(e.y), 2), round(mm(t.GetWidth()), 2))] += 1
    return c
cp3, cp4 = copper(b3), copper(b4)
added, removed = cp4 - cp3, cp3 - cp4
from collections import defaultdict
per = defaultdict(lambda: [0, 0])
xs, ys = [], []
for k, v in added.items():
    per[k[0]][0] += v; xs += [k[2]] + ([k[4]] if len(k) > 4 else []); ys += [k[3]] + ([k[5]] if len(k) > 4 else [])
for k, v in removed.items():
    per[k[0]][1] += v; xs += [k[2]] + ([k[4]] if len(k) > 4 else []); ys += [k[3]] + ([k[5]] if len(k) > 4 else [])
out['copper_per_net'] = {n: v for n, v in sorted(per.items())}
out['copper_change_bbox'] = [min(xs), min(ys), max(xs), max(ys)]
print('copper changes per net (added, removed):', dict(sorted(per.items())))
print('change bbox x %.2f..%.2f y %.2f..%.2f' % (min(xs), max(xs), min(ys), max(ys)))

def via_pad_audit(b):
    vias = []
    for t in b.GetTracks():
        if isinstance(t, p.PCB_VIA):
            s = t.GetStart()
            vias.append((mm(s.x), mm(s.y), mm(t.GetWidth()) / 2, t.GetNetname()))
    pads = []
    for fp in b.GetFootprints():
        for pad in fp.Pads():
            pos = pad.GetPosition()
            sz = pad.GetSize()
            pads.append((mm(pos.x), mm(pos.y), mm(sz.x), mm(sz.y),
                         pad.GetOrientation().AsDegrees(), pad.GetNetname(),
                         fp.GetReference() + '.' + pad.GetNumber()))
    worst = []
    for vx, vy, vr, vn in vias:
        for px, py, sx, sy, rot, pn, ref in pads:
            dx0, dy0 = vx - px, vy - py
            if abs(dx0) > 3 or abs(dy0) > 3:
                continue
            a = math.radians(-rot)
            lx, ly = dx0 * math.cos(a) - dy0 * math.sin(a), dx0 * math.sin(a) + dy0 * math.cos(a)
            ex = max(abs(lx) - sx / 2, 0.0); ey = max(abs(ly) - sy / 2, 0.0)
            gap = math.hypot(ex, ey) - vr
            worst.append((round(gap, 4), vn, ref, pn, round(vx, 2), round(vy, 2)))
    worst.sort()
    return worst
for name, bb in (('rev4', b4), ('rev3', b3)):
    w = via_pad_audit(bb)
    out['via_pad_' + name] = {'min': w[0][0], 'under_0.10': sum(1 for g in w if g[0] < 0.10),
                              'smallest5': [list(x) for x in w[:5]]}
    print('via-pad', name, 'min gap %.4f  pairs<0.10: %d' % (w[0][0], sum(1 for g in w if g[0] < 0.10)))
    for row in w[:3]:
        print('   ', row)
json.dump(out, open('.issue268-runtime/verify4.json', 'w'), indent=1)
print('verify4.json written')
