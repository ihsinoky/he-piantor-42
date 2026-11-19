"""Apply all planned GND taps + FH12 edge bands to the board (pcbnew),
after stripping MUX_EN0/MUX_EN1 (re-routed afterwards around the bands)."""
import pcbnew as p, json, sys, math
from pathlib import Path
E = Path('.').resolve()
SRC = E/'wmain-v4-final.kicad_pcb'
b = p.LoadBoard(str(SRC))
LAY = {p.F_Cu: 'F', p.In1_Cu: 'I1', p.In2_Cu: 'I2', p.B_Cu: 'B'}

# strip EN0/EN1 tracks+vias
kill = [t for t in b.GetTracks() if t.GetNetname() in ('MUX_EN0', 'MUX_EN1')]
for t in kill:
    b.Remove(t)
print('stripped EN items:', len(kill))

gnd = b.FindNet('GND')
def add_via(x, y, d=0.6):
    v = p.PCB_VIA(b)
    v.SetPosition(p.VECTOR2I(round(x * 1e6), round(y * 1e6)))
    v.SetWidth(int(d * 1e6)); v.SetDrill(int(0.3 * 1e6))
    v.SetLayerPair(p.F_Cu, p.B_Cu)
    v.SetNet(gnd)
    v.SetLocked(True)
    b.Add(v)
    return v

def add_seg(x1, y1, x2, y2, w=0.3):
    t = p.PCB_TRACK(b)
    t.SetStart(p.VECTOR2I(round(x1 * 1e6), round(y1 * 1e6)))
    t.SetEnd(p.VECTOR2I(round(x2 * 1e6), round(y2 * 1e6)))
    t.SetWidth(int(w * 1e6)); t.SetLayer(p.F_Cu)
    t.SetNet(gnd); t.SetLocked(True)
    b.Add(t)
    return t

T = json.loads((E/'taps.json').read_text())
nt = 0
for tp in T['taps']:
    add_via(tp['vx'], tp['vy'], tp.get('vd', 0.6))
    add_seg(tp['px'], tp['py'], tp['vx'], tp['vy'], tp.get('sw', 0.3))
    nt += 1
for ch in T.get('chains', []):
    pts = ch['path']
    for i in range(len(pts) - 1):
        add_seg(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], 0.25)
    nt += 1
print('taps applied:', nt)

bands = json.loads((E/'fh12_bands.json').read_text())
for conn, info in bands.items():
    pts = info['band_pts']
    for i in range(len(pts) - 1):
        add_seg(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], 0.25)
    padmap = {}
    for f in b.GetFootprints():
        for pad in f.Pads():
            padmap[f"{f.GetReference()}.{pad.GetNumber()}"] = pad
    for ref, (bx, by) in zip(info['refs'], pts):
        pad = padmap[ref]
        pos = pad.GetPosition()
        add_seg(p.ToMM(pos.x), p.ToMM(pos.y), bx, by, 0.25)
    vx, vy = info['via']
    add_via(vx, vy, 0.5)
    add_seg(pts[-1][0], pts[-1][1], vx, vy, 0.25)
    print(conn, 'band applied, via at', vx, vy)
b.Save(str(E/'wmain-v5-tapped.kicad_pcb'))
print('saved wmain-v5-tapped')
