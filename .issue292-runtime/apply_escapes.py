"""S3a: apply the proven escapes to the tree board.
- escapes_005.json: 12 interior nets, F.Cu tracks w=0.05 + via at end.
- escapes.json: 12 perimeter nets, F.Cu tracks at recorded width + via.
- ANT_LINK: straight segment U1.20-U1.22, w=0.2.
Paths are simplified by EXACT collinear-point removal only (zero
geometry change vs the A*-verified centrelines).
Vias: 0.6/0.3 standard."""
import pcbnew as p, json
from pathlib import Path
E = Path('.').resolve()
TREE = E.parent/'hardware/kicad/qualification/issue-292-wmain'
b = p.LoadBoard(str(TREE/'wmain.kicad_pcb'))

def net(name): return b.FindNet(name)
def add_track(name, x0, y0, x1, y1, w, layer=p.F_Cu):
    t = p.PCB_TRACK(b)
    t.SetNet(net(name))
    t.SetStart(p.VECTOR2I(round(x0 * 1e6), round(y0 * 1e6)))
    t.SetEnd(p.VECTOR2I(round(x1 * 1e6), round(y1 * 1e6)))
    t.SetWidth(int(w * 1e6)); t.SetLayer(layer)
    b.Add(t); return t
def add_via(name, x, y, d=0.6, drill=0.3):
    v = p.PCB_VIA(b)
    v.SetNet(net(name))
    v.SetPosition(p.VECTOR2I(round(x * 1e6), round(y * 1e6)))
    v.SetWidth(int(d * 1e6)); v.SetDrill(int(drill * 1e6))
    v.SetViaType(p.VIATYPE_THROUGH)
    b.Add(v); return v
def simplify(path):
    if len(path) <= 2: return path
    out = [path[0]]
    for i in range(1, len(path) - 1):
        ax, ay = out[-1]; bx, by = path[i]; cx, cy = path[i + 1]
        cross = (bx - ax) * (cy - by) - (by - ay) * (cx - bx)
        if abs(cross) > 1e-9: out.append(path[i])
    out.append(path[-1]); return out

applied = {}
for fname in ('escapes_005.json', 'escapes.json'):
    d = json.loads((E/fname).read_text())
    for name, e in d.items():
        path = simplify([tuple(q) for q in e['path']])
        w = e['width']
        for i in range(len(path) - 1):
            add_track(name, *path[i], *path[i + 1], w)
        vx, vy = e['via']
        add_via(name, vx, vy)
        applied[name] = (len(path) - 1, w, (vx, vy))
        print(name, 'segments', len(path) - 1, 'w', w, 'via', (vx, vy))
add_track('ANT_LINK', 76.4, 124.65, 77.05, 124.65, 0.2)
print('ANT_LINK segment added')
b.Save(str(TREE/'wmain.kicad_pcb'))
print('saved. escapes applied:', len(applied))
