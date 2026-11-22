"""Correction-round probe: pre-trim shelf (99478610a STL) plan
profile near the ends. For 1 mm X columns, intersect the shelf
with the column box at band heights (Z 15..22.5) and report the
Y extent + volume of band material outside the lid span
(|X| > 30.25). Also: shelf bbox, and band material beyond the
outermost cap extent |X| = 151.001."""
import build123d as bd

shelf = bd.import_step("/tmp/shelf-pretrim.step")
bb = shelf.bounding_box()
print(f"shelf bbox X {bb.min.X:.3f}..{bb.max.X:.3f} "
      f"Y {bb.min.Y:.3f}..{bb.max.Y:.3f} Z {bb.min.Z:.3f}..{bb.max.Z:.3f}")
print(f"shelf volume {shelf.volume:.1f}")


def box(xa, xb, ya, yb, za, zb):
    return bd.Solid.make_box(xb - xa, yb - ya, zb - za,
                             bd.Plane(origin=(xa, ya, za)))


for sgn in (+1, -1):
    print(f"--- side {'R' if sgn > 0 else 'L'}: columns from |X| 138")
    e = 138.0
    while e < 154.6:
        xa, xb = (e, e + 1.0) if sgn > 0 else (-e - 1.0, -e)
        col = shelf.intersect(box(xa, xb, -70, 10, 15.0, 22.5))
        cols = list(col) if isinstance(col, (list, bd.ShapeList)) else [col]
        cols = [c for c in cols if c is not None and c.volume > 1e-6]
        if not cols:
            print(f"  |X| {e:6.1f}..{e + 1:6.1f}: -")
        else:
            vol = sum(c.volume for c in cols)
            ys = [c.bounding_box().min.Y for c in cols]
            ye = [c.bounding_box().max.Y for c in cols]
            print(f"  |X| {e:6.1f}..{e + 1:6.1f}: vol {vol:8.1f} "
                  f"Y {min(ys):8.3f}..{max(ye):8.3f} depth {max(ye) - min(ys):6.2f}")
        e += 1.0
    # material beyond the outermost cap extent
    xa, xb = (151.001, 160) if sgn > 0 else (-160, -151.001)
    out = shelf.intersect(box(xa, xb, -70, 10, 0.0, 22.5))
    outs = list(out) if isinstance(out, (list, bd.ShapeList)) else [out]
    outs = [c for c in outs if c is not None and c.volume > 1e-6]
    print(f"  beyond |X| 151.001 (all Z): vol "
          f"{sum(c.volume for c in outs):.1f} in {len(outs)} solids")
