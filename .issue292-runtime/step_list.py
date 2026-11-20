from build123d import import_step
a = import_step('hardware/case/issue-261-lowdeck-full/preview.step')
kids = list(a.children) if hasattr(a, 'children') else [a]
print('top children:', len(kids))
def walk(o, depth=0):
    bb = o.bounding_box()
    lbl = getattr(o, 'label', '') or ''
    print('  '*depth + f"{type(o).__name__} '{lbl}' X[{bb.min.X:.1f},{bb.max.X:.1f}] Y[{bb.min.Y:.1f},{bb.max.Y:.1f}] Z[{bb.min.Z:.1f},{bb.max.Z:.1f}] vol={o.volume:.0f}")
    if depth < 1:
        for c in getattr(o, 'children', []) or []:
            walk(c, depth+1)
for k in kids: walk(k)
