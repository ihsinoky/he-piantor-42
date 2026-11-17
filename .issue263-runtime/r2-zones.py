"""Zone census: count zones by (net, layer) in board file variants."""
import pcbnew as p
from pathlib import Path
from collections import Counter
E = Path('/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation')
RT = Path('/home/hatch/workspace/projects/he-piantor-boards/.issue263-runtime')
for name in ('wing-rev5-16mm-left',):
    for fn, path in (('committed input', RT / 'board-backup' / 'respin-pre' / name / 'input.kicad_pcb'),
                     ('committed main', RT / 'board-backup' / 'respin-pre' / name / 'main.kicad_pcb'),
                     ('respin-in', E / name / 'respin-in.kicad_pcb'),
                     ('routed(new)', E / name / 'routed.kicad_pcb')):
        b = p.LoadBoard(str(path))
        c = Counter((z.GetNetname(), z.GetZoneName()) for z in b.Zones())
        print(name, fn, dict(c), flush=True)
print('done')
