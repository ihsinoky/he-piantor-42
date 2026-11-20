"""Census of the SWD field region on the tree board (read-only)."""
import pcbnew as p
from pathlib import Path
TREE = Path('../hardware/kicad/qualification/issue-292-wmain')
b = p.LoadBoard(str(TREE / 'wmain.kicad_pcb'))
def mm(v): return v / 1e6

print('== JSWD footprint ==')
for f in b.GetFootprints():
    if f.GetReference() == 'JSWD':
        pos = f.GetPosition()
        print('lib:', f.GetFPID().GetLibItemName(), 'pos:', mm(pos.x), mm(pos.y),
              'rot:', f.GetOrientationDegrees(), 'layer:', f.GetLayer())
        for pad in f.Pads():
            pp = pad.GetPosition(); sz = pad.GetSize()
            print(f"  pad {pad.GetNumber()}: net={pad.GetNetname() or '(none)'} "
                  f"@({mm(pp.x):.3f},{mm(pp.y):.3f}) size {mm(sz.x):.3f}x{mm(sz.y):.3f} "
                  f"drill={mm(pad.GetDrillSize().x):.3f}")

print('== tracks/vias in X 104..121, Y 130..139.5 ==')
for t in b.GetTracks():
    pos = t.GetPosition(); x, y = mm(pos.x), mm(pos.y)
    if isinstance(t, p.PCB_VIA):
        if 104 <= x <= 121 and 130 <= y <= 139.5:
            print(f"  VIA {t.GetNetname()} @({x:.3f},{y:.3f}) d={mm(t.GetWidth(p.F_Cu)):.3f} drill={mm(t.GetDrill()):.3f}")
    else:
        s, e = t.GetStart(), t.GetEnd()
        pts = [(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]
        if any(104 <= px <= 121 and 130 <= py <= 139.5 for px, py in pts):
            print(f"  TRK {t.GetNetname()} L={t.GetLayerName()} {pts[0]}->{pts[1]} w={mm(t.GetWidth()):.3f}")

print('== other footprints/pads in the box ==')
for f in b.GetFootprints():
    if f.GetReference() == 'JSWD': continue
    for pad in f.Pads():
        pp = pad.GetPosition(); x, y = mm(pp.x), mm(pp.y)
        if 104 <= x <= 121 and 130 <= y <= 139.5:
            print(f"  {f.GetReference()}.{pad.GetNumber()} net={pad.GetNetname()} @({x:.3f},{y:.3f})")

print('== outline segments with Y > 130 and X in 100..125 ==')
for d in b.GetDrawings():
    if d.GetLayer() == p.Edge_Cuts:
        s, e = d.GetStart(), d.GetEnd()
        pts = [(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]
        if any(100 <= px <= 125 and py > 130 for px, py in pts):
            print('  EDGE', pts)
