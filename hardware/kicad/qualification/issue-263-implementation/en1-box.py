"""Exact foreign F.Cu geometry in the J3.8 escape box + MUX_EN1 target stub."""
import pcbnew as p
from verify import xy

E = '/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation'
b = p.LoadBoard(f'{E}/main-rev8/routed.kicad_pcb')
BOX = (123.0, 109.8, 127.0, 114.2)
def inbox(x, y):
    return BOX[0] <= x <= BOX[2] and BOX[1] <= y <= BOX[3]
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        x, y = xy(t.GetPosition())
        if inbox(x, y):
            print(f'VIA {t.GetNetname()} at ({x:.2f},{y:.2f})')
    elif t.GetLayer() == p.F_Cu:
        a, z = xy(t.GetStart()), xy(t.GetEnd())
        if inbox(*a) or inbox(*z):
            print(f'TRK {t.GetNetname()} w={p.ToMM(t.GetWidth()):.2f} ({a[0]:.3f},{a[1]:.3f}) -> ({z[0]:.3f},{z[1]:.3f})')
for f in b.GetFootprints():
    if f.GetReference() == 'J3':
        for a in f.Pads():
            x, y = xy(a.GetPosition())
            print(f'PAD J3.{a.GetNumber()} {a.GetNetname()} centre ({x:.3f},{y:.3f}) size {[round(p.ToMM(a.GetSize().x),2), round(p.ToMM(a.GetSize().y),2)]} rot {a.GetOrientationDegrees() if hasattr(a,"GetOrientationDegrees") else f.GetOrientationDegrees()}')
