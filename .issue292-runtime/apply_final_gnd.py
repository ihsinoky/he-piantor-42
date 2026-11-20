"""Apply: 4 planned via taps + 2 A* chains (U3.2/U4.2) + module GND
corridor (U1.14/18 stubs, y=121.9 corridor, via at (79.3,121.9),
east drop x=79.15 to U1.7)."""
import pcbnew as p, json
from pathlib import Path
E = Path('.').resolve()
b = p.LoadBoard(str(E/'wmain-v13-final.kicad_pcb'))
gnd = b.FindNet('GND')
LAY = {'F': p.F_Cu, 'I2': p.In2_Cu, 'B': p.B_Cu}

def add_via(x, y, d=0.6, net=None):
    v = p.PCB_VIA(b)
    v.SetPosition(p.VECTOR2I(round(x * 1e6), round(y * 1e6)))
    v.SetWidth(int(d * 1e6)); v.SetDrill(int(0.3 * 1e6))
    v.SetLayerPair(p.F_Cu, p.B_Cu)
    v.SetNet(net or gnd); v.SetLocked(True)
    b.Add(v)

def add_seg(x1, y1, x2, y2, layer='F', w=0.25):
    t = p.PCB_TRACK(b)
    t.SetStart(p.VECTOR2I(round(x1 * 1e6), round(y1 * 1e6)))
    t.SetEnd(p.VECTOR2I(round(x2 * 1e6), round(y2 * 1e6)))
    t.SetWidth(int(w * 1e6)); t.SetLayer(LAY[layer])
    t.SetNet(gnd); t.SetLocked(True)
    b.Add(t)

taps = json.loads((E/'taps_final.json').read_text())
for tp in taps:
    add_via(tp['vx'], tp['vy'], tp['vd'])
    add_seg(tp['px'], tp['py'], tp['vx'], tp['vy'], 'F', 0.3)
print('via taps:', len(taps))

routes = json.loads((E/'astar_routes_multi.json').read_text())
for ref, legs in routes.items():
    for path in legs:
        for i in range(len(path) - 1):
            L1, xa, ya = path[i]; L2, xb, yb = path[i + 1]
            if L1 == L2:
                if abs(xa - xb) > 0.001 or abs(ya - yb) > 0.001:
                    add_seg(xa, ya, xb, yb, L1, 0.25)
            else:
                add_via(xa, ya, 0.5)
    print('chain applied:', ref)

# module corridor
add_seg(77.375, 121.25, 77.375, 121.9, 'F', 0.2)
add_seg(74.775, 121.25, 74.775, 121.9, 'F', 0.2)
add_seg(74.775, 121.9, 79.3, 121.9, 'F', 0.2)
add_via(79.3, 121.9, 0.5)
add_seg(79.15, 121.9, 79.15, 124.525, 'F', 0.2)
add_seg(79.15, 124.525, 78.7, 124.525, 'F', 0.2)
print('corridor applied')
b.Save(str(E/'wmain-v14.kicad_pcb'))
print('saved wmain-v14')
