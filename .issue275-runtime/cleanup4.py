from pathlib import Path
import pcbnew as p
MM = 1e6
BOARD = Path("hardware/kicad/qualification/issue-275-main-rev10/main-rev10/main.kicad_pcb")
b = p.LoadBoard(str(BOARD))
def pt(v):
    return (round(v.x / MM, 3), round(v.y / MM, 3))
n = 0
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA) or t.GetNetname() != "MUX_A1" or t.GetLayer() != p.In2_Cu:
        continue
    if pt(t.GetStart()) == (78.9, 111.8) and pt(t.GetEnd()) == (80.4, 113.3):
        t.SetStart(p.VECTOR2I(round(79.3 * MM), round(112.2 * MM)))
        n += 1
print("shortened:", n)
assert n == 1
filler = p.ZONE_FILLER(b)
filler.Fill(b.Zones())
b.BuildConnectivity()
b.Save(str(BOARD))
print("saved cleanup4")
