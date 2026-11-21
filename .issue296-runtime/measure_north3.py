"""True north-face profile from the BREP solids: intersect tray-right and
strip-right with thin (X,Z) slabs and report Ymin + volume per cell."""
import build123d as bd
import os

ASM = os.path.expanduser("~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d")

def box(x0,x1,y0,y1,z0,z1):
    return bd.Solid.make_box(x1-x0, y1-y0, z1-z0, bd.Plane(origin=(x0,y0,z0)))

for part in ["tray-right","strip-right"]:
    s = bd.import_brep(f"{ASM}/{part}.brep")
    print(f"\n== {part} ==")
    for xst in [40, 60, 80, 100]:
        cells = []
        for z0 in range(-2, 22, 2):
            cell = s.intersect(box(xst-1, xst+1, -70, 5, z0, z0+2))
            cv = sum(c.volume for c in cell) if cell else 0.0
            if cv > 1e-6:
                ymin = min(c.bounding_box().min.Y for c in cell)
                cells.append(f"Z{z0}..{z0+2}: Ymin {ymin:7.2f} (v{cv:6.1f})")
        print(f" X~{xst}:")
        for c in cells: print("   ", c)
