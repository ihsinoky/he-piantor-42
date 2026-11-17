"""17R: dump all HALL_5V copper within 3.5 mm of (116.9, 97.0) on main."""
import pcbnew as p
from pathlib import Path
w = Path('/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation/wing-rev5-17mm-right')
b = p.LoadBoard(str(w / 'main.kicad_pcb'))
TX, TY = 116.9, 97.0
for t in b.GetTracks():
    if t.GetNetname() != 'HALL_5V':
        continue
    s, e = t.GetStart(), t.GetEnd()
    pts = [(p.ToMM(s.x), p.ToMM(s.y)), (p.ToMM(e.x), p.ToMM(e.y))]
    if t.Type() == p.PCB_ARC_T:
        m = t.GetMid()
        pts.append((p.ToMM(m.x), p.ToMM(m.y)))
    if min((x - TX) ** 2 + (y - TY) ** 2 for x, y in pts) ** 0.5 < 3.5:
        print('type', t.Type(), p.LayerName(t.GetLayer()), 'w', round(p.ToMM(t.GetWidth()), 2),
              [(round(x, 2), round(y, 2)) for x, y in pts], t.m_Uuid.AsString()[:8])
for z in b.Zones():
    if z.GetZoneName() == 'Study HALL_5V':
        print('zone HALL_5V layer', p.LayerName(z.GetFirstLayer()))
print('done')
