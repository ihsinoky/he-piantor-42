"""Export the keycap envelope solids (unpressed, Z 10.90..22.00,
from caps.json polygons) as one STL for the P0/P1 renders."""
import build123d as bd
import json, os

RT = os.path.dirname(os.path.abspath(__file__))
ASM = os.path.join(RT, "asm3d")
CAPS = json.load(open(os.path.join(RT, "caps.json")))

solids = []
for side in ("left", "right"):
    for poly in CAPS[side]["cap_polys"]:
        pts = [bd.Vector(p[0], p[1], 0) for p in poly]
        w = bd.Wire.make_polygon(pts + [pts[0]])
        s = bd.extrude(bd.Face(w), 22.00 - 10.90)
        solids.append(s.moved(bd.Location((0, 0, 10.90))))
comp = solids[0]
for s in solids[1:]:
    comp = comp.fuse(s)
bd.export_stl(comp, f"{ASM}/render-caps.stl")
print("caps STL exported:", len(solids), "caps")
