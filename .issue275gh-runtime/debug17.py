import sys, math
src = open('/home/hatch/workspace/projects/he-piantor-ghcheck/.issue275gh-runtime/build_audit.py').read()
head = src.split('wires, lengths, centrelines')[0]
exec(head)
names = sorted(fixed)
print('n fixed:', len(names))
print([n for n in names if 'fly' in n.lower() or 'cable' in n.lower() or 'ezmate' in n.lower() or 'usb' in n.lower()])
bb = fixed[[n for n in names if 'fly' in n.lower()][0]].bounding_box() if any('fly' in n.lower() for n in names) else None
if bb: print('fly bbox:', tuple(round(v, 2) for v in (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)))
