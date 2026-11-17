from pathlib import Path
import pcbnew as p
MM = 1e6
BOARD = Path("hardware/kicad/qualification/issue-275-main-rev10/main-rev10/main.kicad_pcb")
b = p.LoadBoard(str(BOARD))
def pt(v):
    return (round(v.x / MM, 3), round(v.y / MM, 3))
rm = []
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        continue
    s, e = pt(t.GetStart()), pt(t.GetEnd())
    if t.GetNetname() == "MUX_OUT_B" and t.GetLayer() == p.F_Cu and {s, e} in (
            {(88.4, 110.4), (88.4, 105.2)}, {(90.4, 112.4), (88.4, 110.4)}):
        rm.append(t)
    if t.GetNetname() == "MUX_A1" and t.GetLayer() == p.In2_Cu and {s, e} == {(78.9, 111.8), (80.4, 113.3)}:
        rm.append(t)
print("removing:", [(t.GetNetname(), pt(t.GetStart()), pt(t.GetEnd())) for t in rm])
assert len(rm) == 3, len(rm)
for t in rm:
    b.Remove(t)
filler = p.ZONE_FILLER(b)
filler.Fill(b.Zones())
b.BuildConnectivity()
b.Save(str(BOARD))
print("saved cleanup2")
