"""Stage 1 analytic screen: fanout inversion counts for J_WING options.
Row direction in native KiCad frame (left -150 deg, right +150 deg).
Pad order along the row vs destination order (median projection of the
net's other pads onto the row axis). N1 = same order as Rev.4 (pure
translation); N2 = reversed pad order; N3 = bay-facing (row along the
other diagonal) - computed by projecting onto its row axis.
Uses routed.kicad_pcb 17L/17R as the Rev.4 destination reference."""
import re, math, json
from collections import defaultdict

def parse(p):
    t = open(p).read()
    # footprints: reference -> (x,y,rot), pads: (ref, number, net, x, y)
    fps = {}
    # crude s-expr token scan for footprint blocks
    for m in re.finditer(r'\(footprint "([^"]*)".*?\(property "Reference" "([^"]+)"', t, re.S):
        pass
    # simpler: iterate footprint blocks by splitting on '(footprint '
    pads = []
    for blk in t.split('(footprint ')[1:]:
        m = re.search(r'\(at ([\d.-]+) ([\d.-]+)(?: ([\d.-]+))?\)', blk)
        rm = re.search(r'\(property "Reference" "([^"]+)"', blk)
        if not m or not rm: continue
        ref = rm.group(1); fx, fy = float(m.group(1)), float(m.group(2))
        rot = float(m.group(3)) if m.group(3) else 0.0
        # pads: (pad "N" ... (at x y [rot]) ... (net N "NAME")
        for pm in re.finditer(r'\(pad "([^"]+)"[^()]*\(at ([\d.-]+) ([\d.-]+)(?: ([\d.-]+))?\)(.*?)\(net \d+ "([^"]*)"\)', blk, re.S):
            num, px, py = pm.group(1), float(pm.group(2)), float(pm.group(3))
            prot = float(pm.group(4)) if pm.group(4) else 0.0
            net = pm.group(6)
            # rotate local pad offset by footprint rotation (bottom flip ignored for ordering: use magnitude)
            a = math.radians(rot + prot)
            gx = fx + px*math.cos(a) - py*math.sin(a)
            gy = fy + px*math.sin(a) + py*math.cos(a)
            pads.append(dict(ref=ref, num=num, net=net, x=gx, y=gy))
    return pads

def inv(a, b):
    n = len(a); pos = {v: i for i, v in enumerate(b)}
    seq = [pos[v] for v in a]
    return sum(1 for i in range(n) for j in range(i+1, n) if seq[i] > seq[j])

out = {}
for v, rot in (('17mm-left', -150.0), ('17mm-right', 150.0)):
    p = f'/home/hatch/workspace/projects/he-piantor-north/hardware/kicad/qualification/issue-235-wing-round2/wing-rev4-{v}/routed.kicad_pcb'
    pads = parse(p)
    jw = [q for q in pads if q['ref'] == 'J_WING']
    assert len(jw) == 14, (v, len(jw))
    # row axis unit vector in native frame
    a = math.radians(rot)
    ux, uy = math.cos(a), math.sin(a)
    def proj(q): return q['x']*ux + q['y']*uy
    pad_order = [q['num'] for q in sorted(jw, key=proj)]
    # destination: median projection of other pads on same net
    bynet = defaultdict(list)
    for q in pads:
        if q['ref'] != 'J_WING' and q['net']:
            bynet[q['net']].append(proj(q))
    net_of = {q['num']: q['net'] for q in jw}
    dest = {num: sorted(bynet[n])[len(bynet[n])//2] for num, n in net_of.items()}
    dest_order = [num for num, _ in sorted(dest.items(), key=lambda kv: kv[1])]
    base = inv(pad_order, dest_order)
    rev_order = list(reversed(pad_order))
    rev = inv(rev_order, dest_order)
    out[v] = dict(pad_order=pad_order, dest_order=dest_order,
                  inversions_current=base, inversions_reversed=rev,
                  dest_x={k: round(vv, 1) for k, vv in dest.items()})
print(json.dumps(out, indent=1))
