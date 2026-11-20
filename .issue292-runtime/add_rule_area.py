"""S2: add the D-057 rule area MODULE_FIELD_FINE to the tree board.
Rectangle from escape geometry: west vias x=69.6 (r .3 -> 69.3),
east vias 80.6 (-> 80.9), north vias y=119.35 (-> 119.05), south =
footprint body edge 128.85 + .05 -> 128.90. 11.6 x 9.85 = 114.26 mm2.
Rule area on all 4 copper layers (named area for .kicad_dru
InsideArea conditions; no keepout restrictions)."""
import pcbnew as p
from pathlib import Path
E = Path('.').resolve()
TREE = E.parent/'hardware/kicad/qualification/issue-292-wmain'
b = p.LoadBoard(str(TREE/'wmain.kicad_pcb'))
X0, Y0, X1, Y1 = 69.3, 119.05, 80.9, 128.9
# remove any pre-existing area of this name (idempotent)
for z in list(b.Zones()):
    if z.GetZoneName() == 'MODULE_FIELD_FINE':
        b.Remove(z)
for layer in (p.F_Cu, p.In1_Cu, p.In2_Cu, p.B_Cu):
    z = p.ZONE(b)
    z.SetZoneName('MODULE_FIELD_FINE')
    z.SetLayer(layer)
    z.SetIsRuleArea(True)
    z.SetDoNotAllowTracks(False)
    z.SetDoNotAllowVias(False)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowCopperPour(False)
    z.SetDoNotAllowFootprints(False)
    outline = z.Outline()
    outline.NewOutline()
    for (x, y) in [(X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)]:
        outline.Append(int(x * 1e6), int(y * 1e6))
    b.Add(z)
b.Save(str(TREE/'wmain.kicad_pcb'))
print('rule area added: rect', (X0, Y0), (X1, Y1),
      'area mm2 =', round((X1 - X0) * (Y1 - Y0), 2))
