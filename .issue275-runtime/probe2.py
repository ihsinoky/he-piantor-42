from pathlib import Path
import pcbnew as p
MM = 1e6
SRC = Path("/home/hatch/workspace/projects/he-piantor-mainsym/hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb")
b = p.LoadBoard(str(SRC))
fp = b.FindFootprintByReference("J2")
for a in fp.Pads():
    if a.GetNumber() == "1":
        sh = a.GetEffectiveShape(p.F_Cu)
        print(type(sh).__name__)
        out = sh.Outline(0)
        print("points:", out.PointCount())
        for i in range(out.PointCount()):
            pt = out.GetPoint(i)
            print("  ", pt.x / MM, pt.y / MM)
        break
