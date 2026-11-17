"""17R: inspect the HALL_5V via at (116.9, 97.0) overlapping U_HC4.1."""
import pcbnew as p
from pathlib import Path
w = Path('/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation/wing-rev5-17mm-right')
b = p.LoadBoard(str(w / 'main.kicad_pcb'))
TX, TY = 116.9, 97.0
for f in b.GetFootprints():
    if f.GetReference() == 'U_HC4':
        print('U_HC4 at', p.ToMM(f.GetPosition().x), p.ToMM(f.GetPosition().y), 'value', f.GetValue())
        for a in f.Pads():
            print('  pad', a.GetNumber(), a.GetNetname(), 'at', round(p.ToMM(a.GetPosition().x), 3), round(p.ToMM(a.GetPosition().y), 3),
                  'size', round(p.ToMM(a.GetSize().x), 2), round(p.ToMM(a.GetSize().y), 2), 'layers', [p.LayerName(l) for l in a.GetLayerSet().Seq()])
for t in b.GetTracks():
    if t.Type() == p.PCB_VIA_T and abs(p.ToMM(t.GetPosition().x) - TX) < 0.01 and abs(p.ToMM(t.GetPosition().y) - TY) < 0.01:
        print('VIA', t.GetNetname(), 'uuid', t.m_Uuid.AsString())
for t in b.GetTracks():
    s, e = t.GetStart(), t.GetEnd()
    for (x, y) in ((p.ToMM(s.x), p.ToMM(s.y)), (p.ToMM(e.x), p.ToMM(e.y))):
        if abs(x - TX) < 0.01 and abs(y - TY) < 0.01:
            print('track touching via:', t.GetNetname(), p.LayerName(t.GetLayer()),
                  (round(p.ToMM(s.x), 2), round(p.ToMM(s.y), 2)), '->', (round(p.ToMM(e.x), 2), round(p.ToMM(e.y), 2)),
                  'w', round(p.ToMM(t.GetWidth()), 2), 'type', t.Type())
print('done')
