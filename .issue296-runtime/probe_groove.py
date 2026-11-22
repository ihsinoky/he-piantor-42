"""Groove measurement: radial top-height profiles through the
pad centre (0,48) for shell only / shell+cover / assembled,
plus a shell-only height grid over the pad region.
Output: JSON + a compact text summary of profile runs."""
import build123d as bd
import json
import math

ASM = "./asm3d"
PAD = (0.0, 48.0)


def load(name):
    return bd.import_brep(f"{ASM}/{name}.brep")


def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))


def top_at(solids, x, y, half=0.22):
    best = None
    for s in solids:
        cells = s.intersect(box(x - half, x + half, y - half,
                                y + half, -3, 23))
        cells = [c for c in (cells if isinstance(
            cells, (list, bd.ShapeList)) else [cells])
            if c is not None and c.volume > 1e-7]
        for c in cells:
            t = c.bounding_box().max.Z
            if best is None or t > best:
                best = t
    return best


shell = load("shell-central")
cover = load("trackpad-cover")
module = bd.Solid.make_cylinder(20.0, 1.5, bd.Plane(
    origin=(PAD[0], PAD[1], 11.20)))  # Ø40, 11.20..12.70

sets = {"shell": [shell], "shell+cover": [shell, cover],
        "assembled": [shell, cover, module]}

profiles = {}
for name, solids in sets.items():
    prof = {}
    for adeg in range(0, 360, 15):
        a = math.radians(adeg)
        dx, dy = math.cos(a), math.sin(a)
        row = []
        r = 15.0
        while r <= 40.001:
            t = top_at(solids, PAD[0] + dx * r, PAD[1] + dy * r)
            row.append([round(r, 2), None if t is None else round(t, 3)])
            r += 0.25
        prof[adeg] = row
    profiles[name] = prof

# shell-only height grid over the pad region (2 mm pitch)
grid = {}
for gx in range(-34, 35, 2):
    for gy in range(14, 83, 2):
        t = top_at([shell], gx, gy, half=0.9)
        if t is not None:
            grid[f"{gx},{gy}"] = round(t, 3)

json.dump({"profiles": profiles, "grid": grid},
          open("groove-probe.json", "w"))

# summary: for shell+cover and shell, list runs where top < 10.88
for name in ("shell", "shell+cover", "assembled"):
    print(f"== {name}: runs below 10.88 (r-range, min top) ==")
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
print("grid cells not at 10.90 (shell):",
      {k: v for k, v in grid.items() if abs(v - 10.90) > 0.02})
