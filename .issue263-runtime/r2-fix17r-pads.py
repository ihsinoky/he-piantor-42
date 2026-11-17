"""17R only: fix input J_WING pad land 1.50->1.30. Own process."""
import pcbnew as p
from pathlib import Path
w = Path('/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation/wing-rev5-17mm-right')
bi = p.LoadBoard(str(w / 'input.kicad_pcb'))
jw = [f for f in bi.GetFootprints() if f.GetReference() == 'J_WING'][0]
fixed = 0
for a in jw.Pads():
    if a.GetNumber() in [str(i) for i in range(1, 15)]:
        sz = a.GetSize()
        if abs(p.ToMM(sz.y) - 1.3) > 1e-6:
            a.SetSize(p.VECTOR2I(sz.x, p.FromMM(1.3))); fixed += 1
p.SaveBoard(str(w / 'input.kicad_pcb'), bi)
print('17R input pads fixed:', fixed)
