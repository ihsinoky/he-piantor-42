"""Probe the OLD (Stage 3D, commit b3a2b11e7) shell-central for comparison."""
import build123d as bd

def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))

def pieces(r):
    if r is None:
        return []
    xs = list(r) if isinstance(r, (list, bd.ShapeList)) else [r]
    return [x for x in xs if hasattr(x, "volume") and x.volume > 1e-6]

def inter(a, b):
    try:
        return pieces(a.intersect(b))
    except Exception as e:
        print("  intersect error:", e)
        return []

old = bd.import_step("/tmp/oldshell/shell-central.step")
print(f"old shell vol {old.volume/1000:.2f}k  bbox "
      f"X {old.bounding_box().min.X:.2f}..{old.bounding_box().max.X:.2f} "
      f"Y {old.bounding_box().min.Y:.2f}..{old.bounding_box().max.Y:.2f} "
      f"Z {old.bounding_box().min.Z:.2f}..{old.bounding_box().max.Z:.2f}")

print("== OLD shell centre slab X -1..1, per Y bin ==")
for y0 in range(0, 24, 2):
    ps = inter(old, box(-1, 1, y0, y0 + 2, 0, 23))
    if ps:
        zm = max(p.bounding_box().max.Z for p in ps)
        print(f"  Y {y0}..{y0+2}: vol {sum(p.volume for p in ps):8.2f}  top {zm:.2f}")
    else:
        print(f"  Y {y0}..{y0+2}: EMPTY")

print("== OLD shell in X 19..21, Y 20..35 ==")
for p in inter(old, box(19, 21, 20, 35, 0, 23)):
    bb = p.bounding_box()
    print(f"  piece vol {p.volume:8.2f}  X {bb.min.X:.2f}..{bb.max.X:.2f}"
          f"  Y {bb.min.Y:.2f}..{bb.max.Y:.2f}  Z {bb.min.Z:.2f}..{bb.max.Z:.2f}")

print("== OLD shell top near SW1 (X -18..-13, Y 61..68), per 1mm col ==")
for xi in range(-18, -13):
    ps = inter(old, box(xi, xi + 1, 61, 68, 0, 23))
    if ps:
        print(f"  X {xi}..{xi+1}: top {max(p.bounding_box().max.Z for p in ps):.2f}"
              f"  vol {sum(p.volume for p in ps):.2f}")
    else:
        print(f"  X {xi}..{xi+1}: EMPTY")

print("== OLD shell at DLED (-4,13): slab X -5..-3, Y 12..14 ==")
ps = inter(old, box(-5, -3, 12, 14, 0, 23))
for p in ps:
    bb = p.bounding_box()
    print(f"  piece vol {p.volume:8.2f}  Z {bb.min.Z:.2f}..{bb.max.Z:.2f}")
