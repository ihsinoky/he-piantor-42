"""Export helper STLs (internals) for the PO renders."""
import build123d as bd
import json, os

G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
idx = json.load(open(G17 + "/index.json"))
pos = {e["name"]: i for i, e in enumerate(idx)}
ASM = os.path.expanduser("~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d")
ZC = 2.65

def g17(name, dx=0.0):
    s = bd.import_brep(f"{G17}/{pos[name]}.brep")
    return s.moved(bd.Location((dx, 0, -ZC)))

def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))

def fuse_all(ss):
    r = ss[0]
    for s in ss[1:]:
        r = r.fuse(s)
    return r

# Main from D-063 outline
segs = json.load(open(os.path.join(os.path.dirname(__file__),
                                   "main-outline-asm.json")))
pts = [tuple(segs[0][0]), tuple(segs[0][1])]
rest = [tuple(map(tuple, s)) for s in segs[1:]]
while rest:
    for i, (a, b) in enumerate(rest):
        if a == pts[-1]:
            pts.append(b); rest.pop(i); break
        if b == pts[-1]:
            pts.append(a); rest.pop(i); break
    else:
        break
edges = [bd.Edge.make_line(bd.Vector(*pts[i], 0), bd.Vector(*pts[i + 1], 0))
         for i in range(len(pts) - 1)]
wire = bd.Wire(edges)
face = bd.Face(wire)
_s = bd.extrude(face, 1.2)
if _s.bounding_box().max.Z < 0.6:
    _s = bd.extrude(face, -1.2)
main = _s.moved(bd.Location((0, 0, 4.70 - _s.bounding_box().min.Z)))
bd.export_stl(main, f"{ASM}/render-main.stl")

cells = fuse_all([bd.Solid.make_cylinder(7.25, 50.5,
                                         bd.Plane(origin=(cx, -59.62, 7.40),
                                                  z_dir=(0, 1, 0)))
                  for cx in (-15, 0, 15)])
bd.export_stl(cells, f"{ASM}/render-cells.stl")

pb = box(-26.25, 26.25, -62.37, -4.37, -0.65, 0.15)
bd.export_stl(pb, f"{ASM}/render-powerboard.stl")

wings = fuse_all([g17("wing_left", -9.5), g17("wing_right", 9.5),
                  g17("underside-left-J_WING", -9.5),
                  g17("underside-right-J_WING", 9.5),
                  g17("underside-left-U_MUX_B", -9.5),
                  g17("underside-right-U_MUX_B", 9.5)])
bd.export_stl(wings, f"{ASM}/render-wings.stl")
print("render helpers exported")
