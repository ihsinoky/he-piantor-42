from pathlib import Path
import pcbnew as p
MM = 1e6
SRC = Path("/home/hatch/workspace/projects/he-piantor-mainsym/hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb")
b = p.LoadBoard(str(SRC))
for t in b.GetTracks():
    if t.m_Uuid.AsString().startswith("79373271"):
        s, e = t.GetStart(), t.GetEnd()
        print(type(t).__name__, "net", t.GetNetname(), "layer", t.GetLayer(),
              (s.x / MM, s.y / MM), (e.x / MM, e.y / MM), "w", t.GetWidth() / MM)
        if isinstance(t, p.PCB_ARC):
            m = t.GetArcMid()
            print("arc mid", (m.x / MM, m.y / MM))
fp = b.FindFootprintByReference("J2")
for a in fp.Pads():
    if a.GetNumber() == "1":
        pp = a.GetPosition()
        print("pad1 centre", pp.x / MM, pp.y / MM, "size", a.GetSize().x / MM, a.GetSize().y / MM)
