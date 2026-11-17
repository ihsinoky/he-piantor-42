"""R2 fix A (per variant, own process): strip Study zones from respin-in;
apply F3 land correction to input J_WING pads; for 17R also strip routed;
for 17L copy respin-in to routed."""
import pcbnew as p, shutil, sys
from pathlib import Path
E = Path('/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation')
name = sys.argv[1]
w = E / name

def strip_study(b):
    n = 0
    for z in list(b.Zones()):
        if z.GetZoneName() in ('Study HALL_5V', 'Study GND'):
            b.Remove(z); n += 1
    return n

b = p.LoadBoard(str(w / 'respin-in.kicad_pcb'))
removed = strip_study(b)
p.SaveBoard(str(w / 'respin-in.kicad_pcb'), b)
bi = p.LoadBoard(str(w / 'input.kicad_pcb'))
jw = [f for f in bi.GetFootprints() if f.GetReference() == 'J_WING'][0]
fixed = 0
for a in jw.Pads():
    if a.GetNumber() in [str(i) for i in range(1, 15)]:
        sz = a.GetSize()
        if abs(p.ToMM(sz.y) - 1.3) > 1e-6:
            a.SetSize(p.VECTOR2I(sz.x, p.FromMM(1.3))); fixed += 1
p.SaveBoard(str(w / 'input.kicad_pcb'), bi)
print(f'{name}: stripped {removed}; input pads fixed {fixed}', flush=True)
if name == 'wing-rev5-17mm-right':
    br = p.LoadBoard(str(w / 'routed.kicad_pcb'))
    print('17R routed stripped:', strip_study(br), flush=True)
    p.SaveBoard(str(w / 'routed.kicad_pcb'), br)
if name == 'wing-rev5-17mm-left':
    shutil.copyfile(w / 'respin-in.kicad_pcb', w / 'routed.kicad_pcb')
    print('17L routed := respin-in', flush=True)
print('done')
