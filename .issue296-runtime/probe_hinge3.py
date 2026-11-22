"""Probe 3: Wing board bodies vs the planned hinge post boxes
(X 14..18 / 25..28, Y -2.37..-0.37, Z 4..19.3) and vs the stop
post zone (X -3..3, Y 1.88..2.88, Z 10.9..19.1)."""
import build123d as bd
import json

G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
idx = json.load(open(G17 + "/index.json"))
pos = {e["name"]: i for i, e in enumerate(idx)}
ZC = 2.65


def g17(name, dx=0.0):
    s = bd.import_brep(f"{G17}/{pos[name]}.brep")
    return s.moved(bd.Location((dx, 0, -ZC)))


def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))


wings = [g17("wing_right", 9.5), g17("wing_left", -9.5)]
for e in idx:
    if e["name"].startswith("underside-right"):
        wings.append(g17(e["name"], 9.5))
    if e["name"].startswith("underside-left"):
        wings.append(g17(e["name"], -9.5))
W = wings[0]
for w in wings[1:]:
    W = W.fuse(w)

for (xa, xb) in ((14, 18), (25, 28), (-18, -14), (-28, -25)):
    r = W.intersect(box(xa, xb, -2.37, -0.37, 4.0, 19.3))
    r = sum((c for c in (r if isinstance(r, (list, bd.ShapeList)) else [r]) if c is not None), None) if False else r
    v = r.volume if r is not None else 0.0
    print(f"post X {xa}..{xb}: wing intersection {v:.4f} mm3")
r = W.intersect(box(-3, 3, 1.88, 2.88, 10.9, 19.1))
    r = sum((c for c in (r if isinstance(r, (list, bd.ShapeList)) else [r]) if c is not None), None) if False else r
print("stop post zone: wing intersection",
      (r.volume if r is not None else 0.0))
# where is the right Wing's west edge at Y -2.37..-0.37, Z 4.7..5.9?
r = W.intersect(box(0, 60, -2.37, -0.37, 4.7, 5.9))
    r = sum((c for c in (r if isinstance(r, (list, bd.ShapeList)) else [r]) if c is not None), None) if False else r
if r is not None and r.volume > 1e-6:
    bb = r.bounding_box()
    print("wing material in X0..60/Y-2.37..-0.37/Z4.7..5.9: X",
          round(bb.min.X, 2), "..", round(bb.max.X, 2),
          "vol", round(r.volume, 2))
else:
    print("no wing material in X0..60 strip at bay south wall")
