import build123d as bd
ASM = "./asm3d"
def load(n): return bd.import_brep(f"{ASM}/{n}.brep")
def cells_of(r):
    if r is None: return []
    items = list(r) if isinstance(r, (list, bd.ShapeList)) else [r]
    return [c for c in items if c is not None and hasattr(c, "volume") and c.volume > 1e-6]
cover, shell = load("trackpad-cover"), load("shell-central")
inter = cells_of(cover.intersect(shell))
print(f"cover x shell: {len(inter)} cells")
for c in inter:
    bb = c.bounding_box()
    print(f"  vol {c.volume:8.3f}  X {bb.min.X:7.2f}..{bb.max.X:7.2f}  Y {bb.min.Y:7.2f}..{bb.max.Y:7.2f}  Z {bb.min.Z:6.2f}..{bb.max.Z:6.2f}")
