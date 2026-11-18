import sys
src = open('/home/hatch/workspace/projects/he-piantor-ghcheck/.issue275gh-runtime/build_audit.py').read()
head = src.split('# ---------- audit ----------')[0]
exec(head)

def pieces(c):
    if c is None: return []
    try:
        _ = c.volume; items = [c]
    except AttributeError:
        items = list(c)
    out = []
    for s in items:
        b = s.bounding_box()
        out.append((round(float(s.volume), 3),
                    (round(b.min.X, 1), round(b.min.Y, 1), round(b.min.Z, 1),
                     round(b.max.X, 1), round(b.max.Y, 1), round(b.max.Z, 1))))
    return out

for pair in (('R1', 'R2'), ('R13', 'R14'), ('R7', 'R8')):
    c = wires[pair[0]].intersect(wires[pair[1]])
    print(pair, pieces(c))
print('R13 pts:', [(round(p[0], 1), round(p[1], 1)) for p in centrelines['R13']])
print('R14 pts:', [(round(p[0], 1), round(p[1], 1)) for p in centrelines['R14']])
