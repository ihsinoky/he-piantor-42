"""S3a3: apply gnd_taps.json to the tree board (tracks w=0.2 + vias)."""
import pcbnew as p, json
from pathlib import Path
E = Path('.').resolve()
TREE = E.parent/'hardware/kicad/qualification/issue-292-wmain'
b = p.LoadBoard(str(TREE/'wmain.kicad_pcb'))
gnd = b.FindNet('GND')
d = json.loads((E/'gnd_taps.json').read_text())
def simplify(path):
    if len(path) <= 2: return path
    out = [path[0]]
    for i in range(1, len(path) - 1):
        ax, ay = out[-1]; bx, by = path[i]; cx, cy = path[i + 1]
        if abs((bx - ax) * (cy - by) - (by - ay) * (cx - bx)) > 1e-9: out.append(path[i])
    out.append(path[-1]); return out
for num, e in d.items():
    path = simplify([tuple(q) for q in e['path']])
    for i in range(len(path) - 1):
        t = p.PCB_TRACK(b); t.SetNet(gnd)
        t.SetStart(p.VECTOR2I(round(path[i][0] * 1e6), round(path[i][1] * 1e6)))
        t.SetEnd(p.VECTOR2I(round(path[i + 1][0] * 1e6), round(path[i + 1][1] * 1e6)))
        t.SetWidth(int(e['width'] * 1e6)); t.SetLayer(p.F_Cu); b.Add(t)
    if e['via']:
        v = p.PCB_VIA(b); v.SetNet(gnd)
        v.SetPosition(p.VECTOR2I(round(e['via'][0] * 1e6), round(e['via'][1] * 1e6)))
        v.SetWidth(int(0.6 * 1e6)); v.SetDrill(int(0.3 * 1e6)); v.SetViaType(p.VIATYPE_THROUGH)
        b.Add(v)
    print('pad', num, 'applied, via', e['via'], 'target', e['target'])
b.Save(str(TREE/'wmain.kicad_pcb'))
print('saved')
