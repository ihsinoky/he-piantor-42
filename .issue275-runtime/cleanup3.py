from pathlib import Path
import pcbnew as p
MM = 1e6
BOARD = Path("hardware/kicad/qualification/issue-275-main-rev10/main-rev10/main.kicad_pcb")
b = p.LoadBoard(str(BOARD))
netobj = None
for t in b.GetTracks():
    if t.GetNetname() == "MUX_A1":
        netobj = t.GetNet()
        break
t = p.PCB_TRACK(b)
t.SetStart(p.VECTOR2I(round(78.9 * MM), round(111.8 * MM)))
t.SetEnd(p.VECTOR2I(round(80.4 * MM), round(113.3 * MM)))
t.SetWidth(100000)
t.SetLayer(p.In2_Cu)
t.SetNet(netobj)
b.Add(t)
filler = p.ZONE_FILLER(b)
filler.Fill(b.Zones())
b.BuildConnectivity()
b.Save(str(BOARD))
print("restored In2 stub")
