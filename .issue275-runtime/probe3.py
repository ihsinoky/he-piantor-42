from pathlib import Path
import pcbnew as p
SRC = Path("/home/hatch/workspace/projects/he-piantor-mainsym/hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb")
b = p.LoadBoard(str(SRC))
fp = b.FindFootprintByReference("J2")
a = [x for x in fp.Pads() if x.GetNumber() == "1"][0]
sh = a.GetEffectiveShape(p.F_Cu)
print([m for m in dir(sh) if not m.startswith("_")][:40])
print("HitTest centre:", a.HitTest(a.GetPosition(), 0))
import math
c = a.GetPosition()
print("HitTest +0.5mm x:", a.HitTest(p.VECTOR2I(c.x + 500000, c.y), 0))
print("HitTest +0.5mm y:", a.HitTest(p.VECTOR2I(c.x, c.y + 500000), 0))
