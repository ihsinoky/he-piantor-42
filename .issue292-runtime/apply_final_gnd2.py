"""Apply to wmain-v13-final: taps_final 4 via taps + hand vias for
U3.2 (122.3,128.8) d0.5 and U4.2 (118.72,131.5) d0.45."""
import pcbnew as p, json
from pathlib import Path
E = Path('.').resolve()
b = p.LoadBoard(str(E/'wmain-v13-final.kicad_pcb'))
gnd = b.FindNet('GND')

def add_via(x, y, d):
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

taps = json.loads((E/'taps_final.json').read_text())
for tp in taps:
    add_via(tp['vx'], tp['vy'], tp['vd'])
    add_seg(tp['px'], tp['py'], tp['vx'], tp['vy'], 0.3)
print('via taps:', len(taps))
add_via(122.3, 128.8, 0.5)
add_seg(123.66, 128.8, 122.3, 128.8, 0.25)
add_via(118.72, 131.5, 0.45)
add_seg(118.16, 132.0, 118.72, 131.5, 0.25)
print('hand vias applied')
b.Save(str(E/'wmain-v15.kicad_pcb'))
print('saved wmain-v15')
