import csv, io
SRC_BOM = '/home/hatch/workspace/projects/he-piantor-42/hardware/kicad/qualification/issue-182-matrix-rev3/manufacturing/BOM.csv'
SRC_CPL = '/home/hatch/workspace/projects/he-piantor-quote/hardware/kicad/qualification/issue-182-matrix-rev3/manufacturing/CPL-jlcpcb-gerber-frame.csv'
DST = 'hardware/kicad/qualification/issue-268-matrix-rev4/manufacturing/'
FH12 = ('FH12-14S-0.5SH(55)', 'J_WING', 'Hirose_FH12-14S-0.5SH_1x14-1MP_P0.50mm_Horizontal', 'C5378715')
rows = list(csv.reader(open(SRC_BOM)))
hdr, groups = rows[0], []
for r in rows[1:]:
    if r[1] == 'J_WING':
        groups.append(FH12)
    else:
        groups.append(tuple(r))
# per-designator BOM
out = io.StringIO(); w = csv.writer(out, lineterminator='\n')
w.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #'])
n = 0
for comment, desigs, fp, lcsc in groups:
    for d in desigs.split(','):
        w.writerow([comment, d, fp, lcsc]); n += 1
open(DST + 'BOM-jlcpcb.csv', 'w').write(out.getvalue())
# consolidated
out = io.StringIO(); w = csv.writer(out, lineterminator='\n')
w.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #', 'Quantity'])
for comment, desigs, fp, lcsc in groups:
    ds = desigs.split(',')
    w.writerow([comment, ','.join(ds) if len(ds) == 1 else '"%s"' % ','.join(ds), fp, lcsc, len(ds)])
# csv.writer already quotes when needed; rewrite properly:
out = io.StringIO(); w = csv.writer(out, lineterminator='\n')
w.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #', 'Quantity'])
for comment, desigs, fp, lcsc in groups:
    ds = desigs.split(',')
    w.writerow([comment, ','.join(ds), fp, lcsc, len(ds)])
open(DST + 'BOM-jlcpcb-consolidated.csv', 'w').write(out.getvalue())
print('BOM-jlcpcb rows:', n, 'groups:', len(groups))
# CPL
lines = open(SRC_CPL).read().splitlines()
out = []
for ln in lines:
    if ln.startswith('J_WING,'):
        out.append('J_WING,100.000000mm,-134.400000mm,bottom,180.000000')
    else:
        out.append(ln)
open(DST + 'CPL-jlcpcb-gerber-frame.csv', 'w').write('\n'.join(out) + '\n')
print('CPL rows:', len(out) - 1)
