from pathlib import Path
import pcbnew as p
MM = 1e6
for name, path in (("rev9", "hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb"),
                   ("rev10", "hardware/kicad/qualification/issue-275-main-rev10/main-rev10/main.kicad_pcb")):
    b = p.LoadBoard(str(Path("/home/hatch/workspace/projects/he-piantor-mainsym") / path))
    print("==", name)
    for t in b.GetTracks():
        if isinstance(t, p.PCB_VIA):
            continue
        s, e = t.GetStart(), t.GetEnd()
        seg = ((s.x / MM, s.y / MM), (e.x / MM, e.y / MM))
        if t.GetNetname() == "MUX_A2" and any(abs(p[1] - 112.0) < 0.01 for p in seg):
            print("  A2", seg, "L", t.GetLayer())
        if t.GetNetname() == "MUX_OUT_C" and any(abs(p[0] - 78.6) < 0.3 and abs(p[1] - 108.2) < 0.3 for p in seg):
            print("  OUT_C", seg, "L", t.GetLayer())
