"""17R only: strip Study zones from routed.kicad_pcb. Own process."""
import pcbnew as p
from pathlib import Path
w = Path('/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation/wing-rev5-17mm-right')
b = p.LoadBoard(str(w / 'routed.kicad_pcb'))
n = 0
for z in list(b.Zones()):
    if z.GetZoneName() in ('Study HALL_5V', 'Study GND'):
        b.Remove(z); n += 1
p.SaveBoard(str(w / 'routed.kicad_pcb'), b)
print('17R routed stripped:', n)
