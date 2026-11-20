"""Dump cluster-W nets: U1 pads, all items with geometry west of x=82,
and each net's items crossing x=82 (rejoin candidates)."""
import pcbnew as p, json
from collections import defaultdict
b = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
LN = {p.F_Cu: 'F', p.In1_Cu: 'I1', p.In2_Cu: 'I2', p.B_Cu: 'B'}
def mm(v): return v / 1e6
flag = json.load(open('.issue292-runtime/edge-wmain.json'))['flagged']
wnets = sorted({r['net'] for r in flag if r['anchor'][0] < 85 and r['net']})
print('cluster W nets:', wnets)
u1 = [f for f in b.GetFootprints() if f.GetReference() == 'U1'][0]
pads = {}
for pad in u1.Pads():
    q = pad.GetPosition()
    pads.setdefault(pad.GetNetname(), []).append((pad.GetNumber(), round(mm(q.x), 2), round(mm(q.y), 2)))
out = {}
for net in wnets:
    items = []
    for t in b.GetTracks():
        if t.GetNetname() != net: continue
        if isinstance(t, p.PCB_VIA):
            q = t.GetPosition(); x, y = mm(q.x), mm(q.y)
            if x < 82: items.append(('via', round(x, 2), round(y, 2), round(mm(t.GetWidth(p.F_Cu)), 2)))
        else:
            s, e = t.GetStart(), t.GetEnd()
            x1, y1, x2, y2 = mm(s.x), mm(s.y), mm(e.x), mm(e.y)
            if min(x1, x2) < 82:
                items.append(('trk', LN[t.GetLayer()], (round(x1, 2), round(y1, 2)), (round(x2, 2), round(y2, 2)), round(mm(t.GetWidth()), 3)))
    out[net] = {'u1_pads': pads.get(net), 'west_items': items}
    print(f"\n== {net}  U1 pads={pads.get(net)}  west items={len(items)}")
    for it in items: print('   ', it)
json.dump(out, open('.issue292-runtime/west-nets.json', 'w'), indent=1)
