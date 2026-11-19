"""S2.6 prep: add C_0805 footprint; swap C_LDO_IN / C_LDO_OUT to it.

The verified 10 uF part (Samsung CL21A106KAYNNNE, LCSC C15850) is 0805;
the donor capacitor land used at build time is 0603. Swap the two LDO
caps to a standard 0805 land, same centres and pad nets.
Run AFTER routing converges; DRC/repair arbitrates the pad-touch fallout.
"""
import sys
import uuid
from pathlib import Path

import pcbnew

WT = Path('/home/hatch/workspace/projects/he-piantor-wmatrix')
TREE = WT / 'hardware/kicad/qualification/issue-288-wmatrix'
LIB = TREE / 'wmatrix.pretty'
MM = 1e6


def u():
    return str(uuid.uuid4())


fp0805 = LIB / 'C_0805.kicad_mod'
if not fp0805.exists():
    body = (f'(footprint "C_0805"\n\t(version 20241229)\n\t(generator "pcbnew")\n'
            f'\t(generator_version "9.0")\n\t(layer "F.Cu")\n\t(descr "0805 chip land")\n'
            f'\t(property "Reference" "REF**"\n\t\t(at 0 -2.2 0)\n\t\t(layer "F.SilkS")\n\t\t(hide yes)\n\t\t(uuid "{u()}")\n'
            '\t\t(effects (font (size 1 1) (thickness 0.15)))\n\t)\n'
            f'\t(property "Value" "C_0805"\n\t\t(at 0 2.2 0)\n\t\t(layer "F.Fab")\n\t\t(hide yes)\n\t\t(uuid "{u()}")\n'
            '\t\t(effects (font (size 1 1) (thickness 0.15)))\n\t)\n'
            '\t(attr smd)\n')
    for (x0, y0, x1, y1, layer) in ((-1.0, -0.65, 1.0, 0.65, 'F.Fab'), (-1.3, -0.9, 1.3, 0.9, 'F.CrtYd')):
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            body += (f'\t(fp_line (start {ax} {ay}) (end {bx} {by})\n'
                     f'\t\t(stroke (width 0.1) (type solid)) (layer "{layer}") (uuid "{u()}"))\n')
    for num, x in (('1', -0.95), ('2', 0.95)):
        body += (f'\t(pad "{num}" smd rect\n\t\t(at {x} 0)\n\t\t(size 1.0 1.3)\n'
                 f'\t\t(layers "F.Cu" "F.Paste" "F.Mask")\n\t\t(uuid "{u()}")\n\t)\n')
    body += '\t(embedded_fonts no)\n)\n'
    fp0805.write_text(body)
    print('wrote C_0805.kicad_mod')

# NOTE: the 0805 land is E-W (pads along x); the placed 0603 caps are N-S.
# Rotate the replacements 90 deg so pad 1 stays on the same side (north).
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
fps = list(b.GetFootprints())
for ref in ('C_LDO_IN', 'C_LDO_OUT'):
    old = next(f for f in fps if f.GetReference() == ref)
    pos, rot = old.GetPosition(), old.GetOrientationDegrees()
    nets = {p.GetNumber(): p.GetNetname() for p in old.Pads()}
    b.Remove(old)
    nf = pcbnew.FootprintLoad(str(LIB), 'C_0805')
    nf.SetReference(ref)
    nf.SetValue('10uF')
    nf.SetPosition(pos)
    nf.SetOrientationDegrees(rot + 90)
    b.Add(nf)
    for p in nf.Pads():
        if nets.get(p.GetNumber()):
            p.SetNet(b.FindNet(nets[p.GetNumber()]))
    print(ref, 'swapped; pads:', {p.GetNumber(): (round(p.GetPosition().x / MM, 2),
                                                  round(p.GetPosition().y / MM, 2)) for p in nf.Pads()})
b.Save(str(TREE / 'wmatrix.kicad_pcb'))
print('saved')
