"""Per-net pad connectivity from board data (union-find over pads/tracks/vias)."""
import pcbnew as p, sys, json, math
from pathlib import Path
E = Path('.').resolve()
SRC = sys.argv[1] if len(sys.argv) > 1 else str(E/'wmain-routed3.kicad_pcb')
b = p.LoadBoard(SRC)
parent = {}
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]; x = parent[x]
    return x
def union(a, c):
    ra, rc = find(a), find(c)
    if ra != rc:
        parent[ra] = rc

items = []  # (kind, net, layer(s), geometry key points)
pads = []
for f in b.GetFootprints():
    ref = str(f.GetReference())
    for pad in f.Pads():
        net = pad.GetNetname()
        if not net:
            continue
        pos = pad.GetPosition()
        layers = []
        if pad.IsOnLayer(p.F_Cu): layers.append('F')
        if pad.IsOnLayer(p.B_Cu): layers.append('B')
        if pad.IsOnLayer(p.In1_Cu): layers.append('I1')
        if pad.IsOnLayer(p.In2_Cu): layers.append('I2')
        if pad.GetAttribute() == p.PAD_ATTRIB_PTH:
            layers = ['F', 'B', 'I1', 'I2']
        pads.append((f"{ref}.{pad.GetNumber()}", net, p.ToMM(pos.x), p.ToMM(pos.y), layers))
        for L in layers:
            k = (net, L, round(p.ToMM(pos.x), 2), round(p.ToMM(pos.y), 2))
            parent.setdefault(k, k)
            items.append(('pad', k, f"{ref}.{pad.GetNumber()}"))
        # union the pad's own layers (plated/smd on F only; module pads F)
        ks = [(net, L, round(p.ToMM(pos.x), 2), round(p.ToMM(pos.y), 2)) for L in layers]
        for k in ks[1:]:
            union(ks[0], k)

LAYER = {p.F_Cu: 'F', p.In1_Cu: 'I1', p.In2_Cu: 'I2', p.B_Cu: 'B'}
segs = []
for t in b.GetTracks():
    net = t.GetNetname()
    if not net:
        continue
    if isinstance(t, p.PCB_VIA):
        pos = t.GetPosition()
        x, y = round(p.ToMM(pos.x), 2), round(p.ToMM(pos.y), 2)
        ks = []
        for L in ('F', 'I1', 'I2', 'B'):
            k = (net, L, x, y); parent.setdefault(k, k); ks.append(k)
        for k in ks[1:]:
            union(ks[0], k)
        segs.append(('via', net, x, y))
    else:
        s, e = t.GetStart(), t.GetEnd()
        L = LAYER.get(t.GetLayer(), '?')
        x1, y1 = round(p.ToMM(s.x), 2), round(p.ToMM(s.y), 2)
        x2, y2 = round(p.ToMM(e.x), 2), round(p.ToMM(e.y), 2)
        for (x, y) in ((x1, y1), (x2, y2)):
            parent.setdefault((net, L, x, y), (net, L, x, y))
        union((net, L, x1, y1), (net, L, x2, y2))
        segs.append(('seg', net, L, x1, y1, x2, y2))

# union pads with segment endpoints that touch them (same point or within pad box)
def key_of(net, L, x, y):
    return (net, L, x, y)
segpts = {}
for s in segs:
    if s[0] == 'seg':
        segpts.setdefault((s[1], s[2]), []).append((s[3], s[4]))
        segpts.setdefault((s[1], s[2]), []).append((s[5], s[6]))
    else:
        for L in ('F', 'I1', 'I2', 'B'):
            segpts.setdefault((s[1], L), []).append((s[2], s[3]))

# spatial join: pad centre key unions with any seg endpoint within 0.35mm on same layer,
# and with seg bodies passing over the pad (point-segment distance < 0.3)
def pt_seg(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))

seglist = [s for s in segs if s[0] == 'seg']
for (ref, net, x, y, layers) in pads:
    for L in layers:
        pk = (net, L, round(x, 2), round(y, 2))
        for s in seglist:
            if s[1] != net or s[2] != L:
                continue
            if pt_seg(x, y, s[3], s[4], s[5], s[6]) < 0.30:
                union(pk, (net, L, s[3], s[4]))

groups = {}
for (ref, net, x, y, layers) in pads:
    k = (net, layers[0], round(x, 2), round(y, 2))
    groups.setdefault(net, {}).setdefault(find(k), []).append(ref)
report = {}
for net, g in sorted(groups.items()):
    if len(g) > 1:
        report[net] = sorted(g.values(), key=len, reverse=True)
print(json.dumps(report, indent=1))
Path('connectivity.json').write_text(json.dumps(report, indent=1))
