from pathlib import Path
import pcbnew as p
RT = Path("/home/hatch/workspace/projects/he-piantor-mainsym/.issue275-runtime")
bk = p.LoadBoard(str(RT / "rev10-routed.kicad_pcb"))
print("tracks:", len(bk.GetTracks()))
b2 = p.LoadBoard(str(RT / "rev10-fullkrt.kicad_pcb"))
print("tracks2:", len(b2.GetTracks()))
