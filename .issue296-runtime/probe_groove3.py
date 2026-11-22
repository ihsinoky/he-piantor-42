"""Groove analysis v3: fine assembled-top grid from meshes;
find every cell whose assembled top is below the 10.90 field
(outside the seat/window), and map shell-only deviations in
the annulus outside the seat."""
import build123d as bd
import math
from collections import defaultdict

ASM = "./asm3d"
PAD = (0.0, 48.0)


def load(name):
    return bd.import_brep(f"{ASM}/{name}.brep")


def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))


class TopMesh:
    def __init__(self, shape, tol=0.03):
        solids = shape.solids() if hasattr(shape, "solids") else [shape]
        self.v, self.t = [], []
        for s in solids:
            verts, tris = s.tessellate(tol)
            off = len(self.v)
            self.v += [(p.X, p.Y, p.Z) for p in verts]
            self.t += [(a + off, b + off, c + off) for a, b, c in tris]
        self.buckets = defaultdict(list)
        for i, (a, b, c) in enumerate(self.t):
            xs = [self.v[a][0], self.v[b][0], self.v[c][0]]
            ys = [self.v[a][1], self.v[b][1], self.v[c][1]]
            for gx in range(int(min(xs) // 2), int(max(xs) // 2) + 1):
                for gy in range(int(min(ys) // 2),
                                int(max(ys) // 2) + 1):
                    self.buckets[(gx, gy)].append(i)

    def top(self, x, y):
        best = None
        for i in self.buckets.get((int(x // 2), int(y // 2)), []):
            a, b, c = self.t[i]
            (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) = (
                self.v[a], self.v[b], self.v[c])
            d = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
            if abs(d) < 1e-12:
                continue
            w1 = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / d
            w2 = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / d
            w3 = 1 - w1 - w2
            if w1 < -1e-9 or w2 < -1e-9 or w3 < -1e-9:
                continue
            z = w1 * z1 + w2 * z2 + w3 * z3
            if best is None or z > best:
                best = z
        return best


region = box(-42, 42, 6, 90, 7, 16)
shell_m = TopMesh(load("shell-central").intersect(region))
cover_m = TopMesh(load("trackpad-cover").intersect(region))

# assembled top on a 0.5 mm grid; report cells below 10.88 with
# r > 20.4 (outside window) -- clusters
below = []
for gx2 in range(-68, 69):
    for gy2 in range(28, 165):
        x, y = gx2 * 0.5, gy2 * 0.5
        r = math.hypot(x - PAD[0], y - PAD[1])
        if r <= 20.4:
            continue
        vals = [m.top(x, y) for m in (shell_m, cover_m)]
        vals = [v for v in vals if v is not None]
        if not vals:
            continue
        t = max(vals)
        if t < 10.88:
            below.append((x, y, round(t, 3), round(r, 2)))
print("assembled cells below 10.88 (x, y, top, r):", len(below))
for b in below:
    print("  ", b)

# shell-only annulus map r 22.5..34: distinct top values + counts
from collections import Counter
cnt = Counter()
for gx2 in range(-68, 69):
    for gy2 in range(28, 165):
        x, y = gx2 * 0.5, gy2 * 0.5
        r = math.hypot(x - PAD[0], y - PAD[1])
        if not (22.5 < r <= 34):
            continue
        t = shell_m.top(x, y)
        if t is not None:
            cnt[round(t, 2)] += 1
print("shell annulus r22.5..34 top-value histogram:", dict(cnt))
