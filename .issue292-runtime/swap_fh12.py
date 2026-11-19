"""Swap J2/J3 footprints in wmain-v11-routed with the corrected FH12
(pad local rotation 43 -> 0). Pose, reference and pad nets preserved."""
import pcbnew as p
from pathlib import Path
E = Path('.').resolve()
LIB = str((E/'../hardware/kicad/qualification/issue-292-wmain/wmain.pretty').resolve())
b = p.LoadBoard(str(E/'wmain-v11-routed.kicad_pcb'))
for ref in ('J2', 'J3'):
    old = [f for f in b.GetFootprints() if str(f.GetReference()) == ref][0]
    pos = old.GetPosition()
    rot = old.GetOrientation()
    nets = {pad.GetNumber(): pad.GetNet() for pad in old.Pads()}
    layer = old.GetLayer()
    b.Remove(old)
    new = p.FootprintLoad(LIB, 'FH12-14S-0.5SH')
    new.SetReference(ref)
    new.SetPosition(pos)
    new.SetOrientation(rot)
    if layer == p.B_Cu:
        new.Flip(pos, False)
    for pad in new.Pads():
        if pad.GetNumber() in nets:
            pad.SetNet(nets[pad.GetNumber()])
    b.Add(new)
    p1 = [q for q in new.Pads() if q.GetNumber() == '1'][0]
    print(ref, 'swapped; pad1 orient now', p1.GetOrientationDegrees())
b.Save(str(E/'wmain-v12.kicad_pcb'))
print('saved wmain-v12')
