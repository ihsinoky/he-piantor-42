"""Compare J_WING pad sizes: input.kicad_pcb vs corrected .kicad_mod."""
import pcbnew as p
from pathlib import Path
E = Path('/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation')
FP = 'Hirose_FH12-14S-0.5SH_1x14-1MP_P0.50mm_Horizontal'
ref = p.FootprintLoad(str(E / 'connector'), FP)
refmap = {a.GetNumber(): (p.ToMM(a.GetSize().x), p.ToMM(a.GetSize().y)) for a in ref.Pads()}
for name in ('wing-rev5-16mm-left', 'wing-rev5-17mm-right'):
    b = p.LoadBoard(str(E / name / 'input.kicad_pcb'))
    jw = [f for f in b.GetFootprints() if f.GetReference() == 'J_WING'][0]
    diffs = []
    for a in jw.Pads():
        cur = (p.ToMM(a.GetSize().x), p.ToMM(a.GetSize().y))
        if a.GetNumber() in refmap and cur != refmap[a.GetNumber()]:
            diffs.append((a.GetNumber(), cur, refmap[a.GetNumber()]))
    print(name, 'pad size diffs vs corrected footprint:', diffs, flush=True)
print('done')
