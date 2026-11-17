"""R2 fixes:
1. Strip diagnose-generated 'Study *' zones from every respin-in (diagnose
   re-creates them; round-1 inputs carried none).
2. Regenerate definition.json outline_mm from the NOTCHED outline.
3. Apply the F3 land correction (1.50 -> 1.30, centre-anchored) to the
   J_WING signal pads of input.kicad_pcb (qualify reference) x4.
4. 17R: strip Study zones from its finished routed board.
5. 17L: respin-in (notch only) becomes its routed board for diagnose."""
import pcbnew as p, json, shutil
from pathlib import Path
E = Path('/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation')
NAMES = ('wing-rev5-16mm-left', 'wing-rev5-16mm-right', 'wing-rev5-17mm-left', 'wing-rev5-17mm-right')

def strip_study(b):
    n = 0
    for z in list(b.Zones()):
        if z.GetZoneName() in ('Study HALL_5V', 'Study GND'):
            b.Remove(z); n += 1
    return n

for name in NAMES:
    w = E / name
    b = p.LoadBoard(str(w / 'respin-in.kicad_pcb'))
    removed = strip_study(b)
    p.SaveBoard(str(w / 'respin-in.kicad_pcb'), b)
    poly = p.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(poly)
    o = poly.Outline(0)
    pts = [[round(p.ToMM(o.GetPoint(i).x) - 100, 6), round(100 - p.ToMM(o.GetPoint(i).y), 6)]
           for i in range(o.PointCount())]
    d = json.loads((w / 'definition.json').read_text())
    d['outline_mm'] = pts
    (w / 'definition.json').write_text(json.dumps(d, indent=2) + '\n')
    bi = p.LoadBoard(str(w / 'input.kicad_pcb'))
    jw = [f for f in bi.GetFootprints() if f.GetReference() == 'J_WING'][0]
    fixed = 0
    for a in jw.Pads():
        if a.GetNumber() in [str(i) for i in range(1, 15)]:
            sz = a.GetSize()
            if abs(p.ToMM(sz.y) - 1.3) > 1e-6:
                a.SetSize(p.VECTOR2I(sz.x, p.FromMM(1.3))); fixed += 1
    p.SaveBoard(str(w / 'input.kicad_pcb'), bi)
    print(f'{name}: stripped {removed} study zones; outline_mm {len(pts)} pts; input pads fixed {fixed}', flush=True)

w = E / 'wing-rev5-17mm-right'
b = p.LoadBoard(str(w / 'routed.kicad_pcb'))
print('17R routed study zones stripped:', strip_study(b), flush=True)
p.SaveBoard(str(w / 'routed.kicad_pcb'), b)
shutil.copyfile(E / 'wing-rev5-17mm-left' / 'respin-in.kicad_pcb',
                E / 'wing-rev5-17mm-left' / 'routed.kicad_pcb')
print('17L routed := respin-in (notch only)')
print('done')
