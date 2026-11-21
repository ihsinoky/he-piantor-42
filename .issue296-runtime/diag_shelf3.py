import build123d as bd
import json, os
ASM = os.path.expanduser("~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d")
RT = os.path.dirname(os.path.abspath(__file__))
def part(n): return bd.import_brep(f"{ASM}/{n}.brep")
def box(x0,x1,y0,y1,z0,z1):
    return bd.Solid.make_box(x1-x0,y1-y0,z1-z0, bd.Plane(origin=(x0,y0,z0)))
def fuse_all(ss):
    r = ss[0]
    for s in ss[1:]: r = r.fuse(s)
    return r
def inter_vol(a,b):
    try: r = a.intersect(b)
    except Exception: return 0.0
    if r is None: return 0.0
    if isinstance(r,(list,bd.ShapeList)): return sum(x.volume for x in r if hasattr(x,"volume"))
    return r.volume
case_noshelf = fuse_all([part("tray-left"), part("tray-right"), part("centre-infill"),
                         part("shell-central"), part("plate-left"), part("plate-right"),
                         part("plunger-sw1"), part("light-pipe-dled")])
for sgn, nm in ((+1,"east"),(-1,"west")):
    zone = box(22.50,30.25,-59.62,-9.12,7.40,9.40) if sgn>0 else box(-30.25,-22.50,-59.62,-9.12,7.40,9.40)
    print(f"finger working band {nm} (Z 7.40..9.40, inboard): vs case(no shelf) {inter_vol(case_noshelf, zone):.3f}")
CAPS = json.load(open(os.path.join(RT,"caps.json")))
for X in (-55,-85):
    caps = CAPS["left"]["capline"]
    ks = [int(k) for k in caps if abs(int(k)-X) <= 4]
    cl = min(caps[str(k)] for k in ks) if ks else float("nan")
    print(f"screw X {X}: capline near column {cl:.2f}, axis-to-capline {cl-(-61.37):.2f} mm")
