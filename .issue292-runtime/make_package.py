"""Manufacturing package for issue-292-wmain (DRAFT / NOT FOR ORDER):
BOM-jlcpcb.csv (+consolidated), CPL-jlcpcb-gerber-frame.csv from the
final board, gerbers+drill via kicad-cli (run by caller)."""
import pcbnew as p, csv, io
from pathlib import Path
E = Path('.').resolve()
TREE = E/'../hardware/kicad/qualification/issue-292-wmain'
MFG = TREE/'manufacturing'
MFG.mkdir(exist_ok=True)
b = p.LoadBoard(str(TREE/'wmain.kicad_pcb'))

LCSC = {  # only codes verified in repo records; others stay 'verify at quote'
 'TPS63070RNMR': 'C109322', 'TPS22919DCKR': 'C2149796',
 'FH12-14S-0.5SH(55)': 'C5378715', '781710004 (Fly link)': 'C588524',
 '1.5uH XFL4020-152MEC': 'C3033018',
 '100k': 'C25803', '10k': 'C25804', '1k': 'C21190', '100nF': 'C1525', '1nF': 'C1523',
 'ISP1807-LR': 'C5264268',
}
NOPART = {'TP1', 'TP2', 'TP3', 'TP4', 'TP5', 'H1', 'H2', 'H3', 'JSWD', 'JPAD'}
rows = []
cpl = []
for f in b.GetFootprints():
    ref = str(f.GetReference())
    val = str(f.GetValue())
    fp = str(f.GetFPID().GetLibItemName())
    code = LCSC.get(val, '')
    note = ''
    if ref in NOPART:
        note = 'no part (pads/hole only)'
    elif ref == 'U1':
        note = 'JLCPCB Pre-order Part (Extended), est. $11.78, est. lead ~28 days; shelf stock 0 (verified 2026-11-19)'
    elif not code:
        note = 'verify at quote'
    rows.append((val, ref, fp, code, note))
    pos = f.GetPosition()
    cpl.append((ref, p.ToMM(pos.x), -p.ToMM(pos.y), 'top', f.GetOrientationDegrees()))

rows.sort(key=lambda r: r[1])
with open(MFG/'BOM-jlcpcb.csv', 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #', 'Note'])
    for r in rows:
        w.writerow(r)
# consolidated by (value, footprint, code)
from collections import OrderedDict
cons = OrderedDict()
for val, ref, fp, code, note in rows:
    k = (val, fp, code)
    cons.setdefault(k, []).append(ref)
with open(MFG/'BOM-jlcpcb-consolidated.csv', 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #', 'Quantity'])
    for (val, fp, code), refs in cons.items():
        w.writerow([val, ','.join(refs), fp, code, len(refs)])
cpl.sort(key=lambda r: r[0])
with open(MFG/'CPL-jlcpcb-gerber-frame.csv', 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
    for ref, x, y, layer, rot in cpl:
        w.writerow([ref, f'{x:.6f}mm', f'{y:.6f}mm', layer, f'{rot:.6f}'])
print('BOM rows:', len(rows), 'CPL rows:', len(cpl), 'consolidated:', len(cons))
