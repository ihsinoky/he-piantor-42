import build123d as bd, json
G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
idx = json.load(open(G17 + "/index.json"))
def load(i): return bd.import_brep(f"{G17}/{i}.brep")
def solids(s):
    if s is None: return []
    try: return s.solids()
    except AttributeError: return list(s)
def zspans(body, x, y):
    col = bd.Solid.make_box(0.3, 0.3, 40).moved(bd.Location((x-0.15, y-0.15, -5)))
    r = solids(body.intersect(col))
    return [(round(s.bounding_box().min.Z,2), round(s.bounding_box().max.Z,2)) for s in r if s.volume > 0.001]
B = {i: load(i) for i in (221, 4, 336, 337)}
W = [load(i) for i in range(352, 366)]
import math
# scan line: start on old NE diagonal at board (110,88) -> g17 (10,18); heading NE normal (0.866,-0.5)
x0, y0 = 10.0, 18.0; dx, dy = 0.8660254, -0.5
print("dist | tray-right Z | wing_right Z | strip-right Z | shell-central Z | wires Z (union)")
for s in range(0, 41):
    d = s * 0.5
    x, y = x0 + dx*d, y0 + dy*d
    tw = zspans(B[221], x, y); wg = zspans(B[4], x, y)
    sr = zspans(B[336], x, y); sc = zspans(B[337], x, y)
    wz = []
    for w in W: wz += zspans(w, x, y)
    print(f"{d:5.1f} | {tw} | {wg} | {sr} | {sc} | {sorted(set(wz))}")
