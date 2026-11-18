"""Test KiCad connectivity API: walk J2 pads to first via."""
from pathlib import Path
import pcbnew as p

MM = 1e6
SRC = Path("/home/hatch/workspace/projects/he-piantor-mainsym/hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb")
b = p.LoadBoard(str(SRC))
b.BuildConnectivity()
conn = b.GetConnectivity()
fp = b.FindFootprintByReference("J2")
for a in sorted(fp.Pads(), key=lambda q: q.GetNumber()):
    vt = p.KICAD_T_vector()
    for t in (p.PCB_PAD_T, p.PCB_TRACE_T, p.PCB_VIA_T, p.PCB_ARC_T):
        vt.append(t)
    items = conn.GetConnectedItems(a, vt)
    desc = []
    for it in items:
        if isinstance(it, p.PCB_VIA):
            pp = it.GetPosition()
            desc.append(f"VIA@{pp.x/MM:.2f},{pp.y/MM:.2f}")
        elif isinstance(it, p.PAD):
            desc.append(f"PAD {it.GetParentFootprint().GetReference()}.{it.GetNumber()}")
        else:
            s, e = it.GetStart(), it.GetEnd()
            desc.append(f"TRK L{it.GetLayer()} ({s.x/MM:.2f},{s.y/MM:.2f})->({e.x/MM:.2f},{e.y/MM:.2f}) w{it.GetWidth()/MM:.2f}")
    print(a.GetNumber(), a.GetNetname(), "->", len(items))
    for d in desc[:6]:
        print("   ", d)
