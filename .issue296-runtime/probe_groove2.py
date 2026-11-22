"""Groove measurement v2 (mesh-based, fast).

Clips shell + cover breps to the pad region, tessellates, and
samples top heights along radial rays through the pad centre
(0,48) for shell / shell+cover / assembled (module analytic),
plus a shell-only height grid. Prints groove runs."""
import build123d as bd
import json
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
        self.v = []
        self.t = []
        for s in solids:
            verts, tris = s.tessellate(tol)
            off = len(self.v)
            self.v += [(p.X, p.Y, p.Z) for p in verts]
            self.t += [(a + off, b + off, c + off)
                       for (a, b, c) in tris]
        self.buckets = defaultdict(list)
        for i, (a, b, c) in enumerate(tris):
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
print("mesh tris:", len(shell_m.t), len(cover_m.t))


def top_of(meshes, x, y):
    vals = [m.top(x, y) for m in meshes]
    vals = [v for v in vals if v is not None]
    return max(vals) if vals else None


def module_top(r):
    return 12.70 if r <= 20.0 else None


sets = {"shell": [shell_m], "shell+cover": [shell_m, cover_m],
        "assembled": [shell_m, cover_m]}
profiles = {}
for name, meshes in sets.items():
    prof = {}
    for adeg in range(0, 360, 15):
        a = math.radians(adeg)
        dx, dy = math.cos(a), math.sin(a)
        row = []
        r = 14.0
        while r <= 40.001:
            t = top_of(meshes, PAD[0] + dx * r, PAD[1] + dy * r)
            if name == "assembled":
                mt = module_top(r)
                if mt is not None:
                    t = mt if t is None else max(t, mt)
            row.append([round(r, 2), None if t is None else round(t, 3)])
            r += 0.25
        prof[adeg] = row
    profiles[name] = prof

grid = {}
for gx in range(-36, 37, 1):
    for gy in range(12, 85, 1):
        t = shell_m.top(gx, gy)
        if t is not None:
            grid[f"{gx},{gy}"] = round(t, 3)

json.dump({"profiles": profiles, "grid": grid},
          open("groove-probe.json", "w"))

for name in ("shell", "shell+cover", "assembled"):
    print(f"== {name}: runs below 10.88 ==")
    for adeg, row in profiles[name].items():
        run = None
        for r, t in row:
            low = t is not None and t < 10.88
            if low and run is None:
                run = [r, r, t]
            elif low:
                run[1] = r
                run[2] = min(run[2], t)
            elif run is not None:
                print(f"  az{adeg:3d}: r {run[0]:.2f}..{run[1]:.2f} "
                      f"min {run[2]:.3f}")
                run = None
        if run is not None:
            print(f"  az{adeg:3d}: r {run[0]:.2f}..{run[1]:.2f} "
                  f"min {run[2]:.3f}")

# profile dumps at the 4 cardinal + 2 diagonal azimuths (assembled)
for adeg in (0, 90, 180, 270, 30, 210):
    row = profiles["assembled"][adeg]
    print(f"assembled az{adeg}: " +
          " ".join(f"{r}:{t}" for r, t in row if r >= 19.0))
dev = {k: v for k, v in grid.items() if abs(v - 10.90) > 0.02}
print("shell grid cells != 10.90:", len(dev))
for k in sorted(dev):
    print("  ", k, dev[k])
