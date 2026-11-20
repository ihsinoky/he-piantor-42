import pcbnew as p, math
from pathlib import Path
W = Path('..').resolve()
b = p.LoadBoard(str(W/'hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb'))
for f in b.GetFootprints():
    ref = str(f.GetReference())
    if ref in ('CVAUX', 'JPAD', 'RPG', 'COUT1'):
        for a in f.Pads():
            px, py = p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y)
            r = max(p.ToMM(a.GetSize().x), p.ToMM(a.GetSize().y)) / 2
            d = math.hypot(px - 100, py - 118) - r
            print(ref, a.GetNumber(), f"pad edge dist to centre {d:.2f} (clearance to r20: {d - 20:+.2f})")
