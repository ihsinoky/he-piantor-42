from pathlib import Path
import pcbnew as p
BOARD = Path("hardware/kicad/qualification/issue-275-main-rev10/main-rev10/main.kicad_pcb")
b = p.LoadBoard(str(BOARD))
n = 0
for t in b.GetTracks():
    if t.IsLocked():
        t.SetLocked(False); n += 1
print("unlocked:", n)
b.Save(str(BOARD))
