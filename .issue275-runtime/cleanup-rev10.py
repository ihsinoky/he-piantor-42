from pathlib import Path
import pcbnew as p
MM = 1e6
BOARD = Path("hardware/kicad/qualification/issue-275-main-rev10/main-rev10/main.kicad_pcb")
b = p.LoadBoard(str(BOARD))
def pt(v):
    return (round(v.x / MM, 3), round(v.y / MM, 3))
rm = []
for t in b.GetTracks():
    s, e = pt(t.GetStart()), pt(t.GetEnd())
    if isinstance(t, p.PCB_VIA):
        if (t.GetNetname(), s) in (("GND", (77.5, 111.7)), ("MUX_A1", (78.9, 111.8))):
            rm.append(t)
    elif t.GetNetname() == "MUX_OUT_B" and t.GetLayer() == p.F_Cu and {s, e} in (
            {(87.1, 103.9), (83.5, 103.9)}, {(88.4, 105.2), (87.1, 103.9)}):
        rm.append(t)
print("removing:", [(t.GetNetname(), pt(t.GetStart())) for t in rm])
assert len(rm) == 4, len(rm)
for t in rm:
    b.Remove(t)
filler = p.ZONE_FILLER(b)
filler.Fill(b.Zones())
b.BuildConnectivity()
b.Save(str(BOARD))
print("saved cleanup")
