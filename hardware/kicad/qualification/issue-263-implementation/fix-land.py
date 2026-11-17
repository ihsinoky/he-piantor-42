"""F3 correction (actually applied): FH12 signal land length 1.50 -> 1.30 mm,
centre-anchored (pad positions unchanged), per Hirose catalog CL586-0533-0
recommended land pattern 1.3 +/- 0.1. Applies to the .kicad_mod source and
the embedded J2/J3/J_WING footprints in all built boards."""
import glob
import pcbnew as p

E = '/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation'
FILES = [
    f'{E}/main-rev8/input.kicad_pcb', f'{E}/main-rev8/routed.kicad_pcb',
    f'{E}/main-rev8/main.kicad_pcb', f'{E}/inspection/final/main.kicad_pcb',
] + sorted(glob.glob(f'{E}/wing-rev5-*/main.kicad_pcb')) + sorted(glob.glob(f'{E}/wing-rev5-*/routed.kicad_pcb'))
REFS = ('J2', 'J3', 'J_WING')
for path in FILES:
    b = p.LoadBoard(path)
    changed = 0
    for f in b.GetFootprints():
        if f.GetReference() not in REFS:
            continue
        for a in f.Pads():
            if a.GetNumber() in [str(i) for i in range(1, 15)]:
                s = a.GetSize()
                if abs(p.ToMM(s.y) - 1.5) < 0.01:
                    a.SetSize(p.VECTOR2I(s.x, p.FromMM(1.3)))
                    changed += 1
    if changed:
        p.SaveBoard(path, b)
    print(path.split('/')[-2] + '/' + path.split('/')[-1], 'pads corrected:', changed)
print('done')
