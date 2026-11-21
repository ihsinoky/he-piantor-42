"""Probe the shell-central south face C_shell(X) at 0.25 mm sampling,
|X| <= 42, full Z and in the field band Z 8.9..10.9; also the shell
material Z range at its south face columns. For the plan-A build."""
import build123d as bd
import json, os

ASM = os.path.expanduser("~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d")
RT = os.path.dirname(os.path.abspath(__file__))

def part(name):
    return bd.import_brep(f"{ASM}/{name}.brep")

def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))

def cells_of(r):
    if r is None:
        return []
    return [x for x in (list(r) if isinstance(r, (list, bd.ShapeList)) else [r])
            if hasattr(x, "volume") and x.volume > 1e-9]

shell = part("shell-central")
rows = []
x = 0.0
while x <= 42.0:
    cs = cells_of(shell.intersect(box(x, x + 0.25, 55.0, 75.0, -3.0, 23.0)))
    cf = cells_of(shell.intersect(box(x, x + 0.25, 55.0, 75.0, 8.9, 10.9)))
    rows.append([round(x + 0.125, 3),
                 None if not cs else round(max(c.bounding_box().max.Y for c in cs), 3),
                 None if not cf else round(max(c.bounding_box().max.Y for c in cf), 3),
                 None if not cs else round(min(c.bounding_box().min.Z for c in cs), 2),
                 None if not cs else round(max(c.bounding_box().max.Z for c in cs), 2)])
    x += 0.25
json.dump(rows, open(os.path.join(RT, "probe_shell.json"), "w"))
for r in rows:
    print(r)
print("saved probe_shell.json", flush=True)
