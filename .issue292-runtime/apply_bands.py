"""Re-apply FH12 edge bands (locked GND) onto wmain-v7."""
import pcbnew as p, json
from pathlib import Path
E = Path('.').resolve()
b = p.LoadBoard(str(E/'wmain-v10.kicad_pcb'))
gnd = b.FindNet('GND')

def add_via(x, y, d=0.5):
    v = p.PCB_VIA(b)
    v.SetPosition(p.VECTOR2I(round(x * 1e6), round(y * 1e6)))
    v.SetWidth(int(d * 1e6)); v.SetDrill(int(0.3 * 1e6))
    v.SetLayerPair(p.F_Cu, p.B_Cu)
    v.SetNet(gnd); v.SetLocked(True)
    b.Add(v)

def add_seg(x1, y1, x2, y2, w=0.25):
    t = p.PCB_TRACK(b)
    t.SetStart(p.VECTOR2I(round(x1 * 1e6), round(y1 * 1e6)))
    t.SetEnd(p.VECTOR2I(round(x2 * 1e6), round(y2 * 1e6)))
    t.SetWidth(int(w * 1e6)); t.SetLayer(p.F_Cu)
    t.SetNet(gnd); t.SetLocked(True)
    b.Add(t)

bands = json.loads((E/'fh12_bands.json').read_text())
padmap = {}
for f in b.GetFootprints():
    for pad in f.Pads():
        padmap[f"{f.GetReference()}.{pad.GetNumber()}"] = pad
for conn, info in bands.items():
    pts = info['band_pts']
    for i in range(len(pts) - 1):
        add_seg(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1])
    for ref, (bx, by) in zip(info['refs'], pts):
        pos = padmap[ref].GetPosition()
        add_seg(p.ToMM(pos.x), p.ToMM(pos.y), bx, by)
    vx, vy = info['via']
    add_via(vx, vy)
    add_seg(pts[-1][0], pts[-1][1], vx, vy)
    print(conn, 'band re-applied')
b.Save(str(E/'wmain-v10.kicad_pcb'))
print('saved')
