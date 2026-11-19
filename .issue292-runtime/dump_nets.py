"""Dump full geometry of the 5 residual nets from a board file."""
import pcbnew as p, sys, json
from pathlib import Path
SRC = sys.argv[1]
TARGETS = {'GND', 'VBUS', 'SYS_3V3', 'PAD_EN', 'VBAT_SENSE'}
b = p.LoadBoard(SRC)
LAY = {p.F_Cu: 'F', p.In1_Cu: 'I1', p.In2_Cu: 'I2', p.B_Cu: 'B'}
def mm(v): return round(p.ToMM(v), 3)
out = {n: {'pads': [], 'tracks': [], 'vias': [], 'zones': []} for n in TARGETS}
for f in b.GetFootprints():
    ref = str(f.GetReference())
    for pad in f.Pads():
        net = pad.GetNetname()
        if net not in TARGETS: continue
        # only U1 pads for GND (the pair), all pads otherwise
        if net == 'GND' and ref != 'U1': continue
        pos = pad.GetPosition(); sz = pad.GetSize()
        lays = [LAY[l] for l in (p.F_Cu, p.In1_Cu, p.In2_Cu, p.B_Cu) if pad.IsOnLayer(l)]
        out[net]['pads'].append({'id': f"{ref}.{pad.GetNumber()}", 'x': mm(pos.x), 'y': mm(pos.y),
                                 'w': mm(sz.x), 'h': mm(sz.y), 'layers': lays,
                                 'pth': pad.GetAttribute() == p.PAD_ATTRIB_PTH})
for t in b.GetTracks():
    net = t.GetNetname()
    if net not in TARGETS: continue
    if isinstance(t, p.PCB_VIA):
        pos = t.GetPosition()
        out[net]['vias'].append({'x': mm(pos.x), 'y': mm(pos.y), 'dia': mm(t.GetWidth()),
                                 'drill': mm(t.GetDrill()), 'lt': LAY.get(t.TopLayer()), 'lb': LAY.get(t.BottomLayer())})
    else:
        s, e = t.GetStart(), t.GetEnd()
        out[net]['tracks'].append({'layer': LAY.get(t.GetLayer()), 'w': mm(t.GetWidth()),
                                   'x1': mm(s.x), 'y1': mm(s.y), 'x2': mm(e.x), 'y2': mm(e.y)})
for z in b.Zones():
    net = z.GetNetname()
    if net in TARGETS:
        bb = z.GetBoundingBox()
        out[net]['zones'].append({'layer': LAY.get(z.GetLayer()), 'bbox': [mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())]})
json.dump(out, open(sys.argv[2], 'w'), indent=1)
for n in TARGETS:
    d = out[n]
    print(f"{n}: pads {len(d['pads'])} tracks {len(d['tracks'])} vias {len(d['vias'])} zones {len(d['zones'])}")
