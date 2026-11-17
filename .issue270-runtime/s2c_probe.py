"""Probe J2/J3 footprint drawing layers + courtyard; extract Rev.9 outline."""
import json, math, sys
from pathlib import Path
import pcbnew as p
sys.path.insert(0, str(Path(__file__).resolve().parent))
from geom2b import outline_of

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BOARD = ROOT / 'hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb'
MM = 1e6

b = p.LoadBoard(str(BOARD))
out = {}
for ref in ('J2', 'J3'):
    f = [x for x in b.GetFootprints() if x.GetReference() == ref][0]
    layers = {}
    items = []
    for d in f.GraphicalItems():
        lay = d.GetLayerName()
        layers[lay] = layers.get(lay, 0) + 1
        try:
            s, e = d.GetStart(), d.GetEnd()
            items.append((lay, str(d.GetShape()), [s.x / MM - 100, s.y / MM - 70],
                          [e.x / MM - 100, e.y / MM - 70]))
        except Exception:
            items.append((lay, str(d.GetShape()), None, None))
    cy = []
    for li in (0, 1):
        try:
            ps = f.GetCourtyard(li)
            for i in range(ps.OutlineCount()):
                ring = [(ps.Outline(i).CPoint(j).x / MM - 100,
                         ps.Outline(i).CPoint(j).y / MM - 70)
                        for j in range(ps.Outline(i).PointCount())]
                cy.append((li, ring))
        except Exception as ex:
            cy.append((li, str(ex)))
    out[ref] = dict(layers=layers, items=items, courtyard=cy)
    print(ref, 'layers', layers, 'courtyard parts', len(cy))

poly = outline_of(b)
ring = [[round(x - 100, 4), round(y - 70, 4)] for x, y in poly.exterior.coords]
out['rev9_outline_case'] = ring
print('rev9 outline pts', len(ring), 'area', round(poly.area, 2))
json.dump(out, open(HERE / 'stage2c-probe.json', 'w'), indent=1)
print('saved')
