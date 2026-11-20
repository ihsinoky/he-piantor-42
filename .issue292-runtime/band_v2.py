"""FH12 GND v2: remove F bands; per GND pad an outward F stub + own
0.5/0.3 via (plane connection). No continuous band -> signal escapes
cross freely between stubs."""
import pcbnew as p, math
from pathlib import Path
E = Path('.').resolve()
b = p.LoadBoard(str(E/'wmain-v10-routed3.kicad_pcb'))
gnd = b.FindNet('GND')

RECTS = [(70.5, 79.5, 107.0, 115.5), (120.5, 129.5, 107.0, 115.5)]
def in_rect(x, y):
    return any(r[0] <= x <= r[1] and r[2] <= y <= r[3] for r in RECTS)

# remove F.Cu GND tracks + GND vias inside the rects (the F band)
kill = []
for t in b.GetTracks():
    if t.GetNetname() != 'GND':
        continue
    if isinstance(t, p.PCB_VIA):
        pos = t.GetPosition()
        if in_rect(p.ToMM(pos.x), p.ToMM(pos.y)):
            kill.append(t)
    elif t.GetLayer() == p.F_Cu:
        s, e = t.GetStart(), t.GetEnd()
        if in_rect(p.ToMM(s.x), p.ToMM(s.y)) and in_rect(p.ToMM(e.x), p.ToMM(e.y)):
            kill.append(t)
for t in kill:
    b.Remove(t)
print('band items removed:', len(kill))

OUTN = {'J2': (0.681, 0.732), 'J3': (-0.681, 0.732)}
for f in b.GetFootprints():
    ref = str(f.GetReference())
    if ref not in OUTN:
        continue
    nx, ny = OUTN[ref]
    for pad in f.Pads():
        if pad.GetNetname() != 'GND':
            continue
        pos = pad.GetPosition()
        cx, cy = p.ToMM(pos.x), p.ToMM(pos.y)
        vx, vy = cx + 1.05 * nx, cy + 1.05 * ny
        t = p.PCB_TRACK(b)
        t.SetStart(p.VECTOR2I(round(cx * 1e6), round(cy * 1e6)))
        t.SetEnd(p.VECTOR2I(round(vx * 1e6), round(vy * 1e6)))
        t.SetWidth(int(0.25 * 1e6)); t.SetLayer(p.F_Cu)
        t.SetNet(gnd); t.SetLocked(True)
        b.Add(t)
        v = p.PCB_VIA(b)
        v.SetPosition(p.VECTOR2I(round(vx * 1e6), round(vy * 1e6)))
        v.SetWidth(int(0.5 * 1e6)); v.SetDrill(int(0.3 * 1e6))
        v.SetLayerPair(p.F_Cu, p.B_Cu)
        v.SetNet(gnd); v.SetLocked(True)
        b.Add(v)
        print(ref, pad.GetNumber(), 'stub+via at', round(vx, 2), round(vy, 2))
b.Save(str(E/'wmain-v11.kicad_pcb'))
print('saved wmain-v11')
