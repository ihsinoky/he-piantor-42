"""S3a-final apply: escapes_final.json -> tree board.
Entry shapes: T1/T1b {path, via, width} on F; T2/T3 {parts[F,B],
drop_via, end}. Plus ANT_LINK straight segment w=0.2.
Exact collinear simplification only."""
import pcbnew as p, json
from pathlib import Path
E = Path('.').resolve()
TREE = E.parent/'hardware/kicad/qualification/issue-292-wmain'
b = p.LoadBoard(str(TREE/'wmain.kicad_pcb'))
LAY = {'F': p.F_Cu, 'I2': p.In2_Cu, 'B': p.B_Cu}
def add_track(name, x0, y0, x1, y1, w, layer):
    t = p.PCB_TRACK(b); t.SetNet(b.FindNet(name))
    t.SetStart(p.VECTOR2I(round(x0 * 1e6), round(y0 * 1e6)))
    t.SetEnd(p.VECTOR2I(round(x1 * 1e6), round(y1 * 1e6)))
    t.SetWidth(int(w * 1e6)); t.SetLayer(layer); b.Add(t)
def add_via(name, x, y):
    v = p.PCB_VIA(b); v.SetNet(b.FindNet(name))
    v.SetPosition(p.VECTOR2I(round(x * 1e6), round(y * 1e6)))
    v.SetWidth(int(0.6 * 1e6)); v.SetDrill(int(0.3 * 1e6)); v.SetViaType(p.VIATYPE_THROUGH)
    b.Add(v)
def simplify(path):
    if len(path) <= 2: return path
    out = [path[0]]
    for i in range(1, len(path) - 1):
        ax, ay = out[-1]; bx, by = path[i]; cx, cy = path[i + 1]
        if abs((bx - ax) * (cy - by) - (by - ay) * (cx - bx)) > 1e-9: out.append(path[i])
    out.append(path[-1]); return out
d = json.loads((E/'escapes_final.json').read_text())
for name, e in d.items():
    if 'parts' in e:
        for part in e['parts']:
            path = simplify([tuple(q) for q in part['path']])
            for i in range(len(path) - 1):
                add_track(name, *path[i], *path[i + 1], part['width'], LAY[part['layer']])
        add_via(name, *e['drop_via'])
        print(name, 'tier', e['tier'], 'drop via', e['drop_via'], 'end', e['end'])
    else:
        path = simplify([tuple(q) for q in e['path']])
        for i in range(len(path) - 1):
            add_track(name, *path[i], *path[i + 1], e['width'], p.F_Cu)
        add_via(name, *e['via'])
        print(name, 'tier', e.get('tier', '1'), 'via', e['via'], 'w', e['width'])
add_track('ANT_LINK', 76.4, 124.65, 77.05, 124.65, 0.2, p.F_Cu)
print('ANT_LINK applied')
b.Save(str(TREE/'wmain.kicad_pcb'))
print('saved')
