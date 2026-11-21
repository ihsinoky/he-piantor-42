"""Extract switch-hole centres + per-key angles from the built plates
(section at mid-plate), build keycap envelopes (16.5mm squares at each
key's own angle — 17mm pitch class, cf. g17 switch envelope 15.8mm),
and compute the capline (northernmost cap edge per 1mm X column).
Output: caps.json (centres, angles, polygons, capline)."""
import build123d as bd
import numpy as np, json, os, math

ASM = os.path.expanduser("~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d")
RT = os.path.dirname(os.path.abspath(__file__))
CAP = 16.5

def box(x0,x1,y0,y1,z0,z1):
    return bd.Solid.make_box(x1-x0, y1-y0, z1-z0, bd.Plane(origin=(x0,y0,z0)))

def keys_of(part):
    slab = part.intersect(box(-200,200,-200,200,10.0,10.3))
    solids = list(slab) if isinstance(slab,(list,bd.ShapeList)) else [slab]
    keys, others = [], []
    for s in solids:
        for f in s.faces():
            if abs(f.normal_at().Z - 1) < 1e-6 and f.center().Z > 10.2:
                for w in f.inner_wires():
                    vs = [(v.X, v.Y) for v in w.vertices()]
                    bb = w.bounding_box()
                    dx, dy = bb.max.X-bb.min.X, bb.max.Y-bb.min.Y
                    if 17.0 < dx < 21.5 and 17.0 < dy < 21.5:
                        C = np.array([(bb.min.X+bb.max.X)/2, (bb.min.Y+bb.max.Y)/2])
                        V = np.array(vs)
                        d = np.hypot(*(V - C).T)
                        corner = math.degrees(math.atan2(*(V[d.argmax()] - C)[::-1]))
                        ang = (corner - 45.0) % 90
                        keys.append((float(C[0]), float(C[1]), ang, dx))
                    else:
                        others.append((float((bb.min.X+bb.max.X)/2),
                                       float((bb.min.Y+bb.max.Y)/2), dx, dy))
    return keys, others

def capline(keys):
    line, polys = {}, []
    for (cx, cy, ang) in keys:
        th = math.radians(ang)
        u = np.array([math.cos(th), math.sin(th)])
        v = np.array([-math.sin(th), math.cos(th)])
        C = np.array([cx, cy])
        corners = [C + (a*u + b*v)*(CAP/2) for a in (-1,1) for b in (-1,1)]
        # order corners as a loop (sort by polar angle around centre)
        corners.sort(key=lambda p: math.atan2((p-C)[1], (p-C)[0]))
        polys.append([list(map(float, p)) for p in corners])
        pts = []
        for i in range(4):
            p0, p1 = corners[i], corners[(i+1) % 4]
            for t in np.linspace(0, 1, 48):
                pts.append(p0 + (p1-p0)*t)
        for p in pts:
            k = int(math.floor(p[0]))
            if k not in line or p[1] < line[k]:
                line[k] = float(p[1])
    return line, polys

out = {}
for side in ("left","right"):
    plate = bd.import_brep(f"{ASM}/plate-{side}.brep")
    keys, others = keys_of(plate)
    # snap main-grid keys (hole bbox 19.00) to the median angle; thumb keys
    # (different bbox) keep their individual angles
    main = [k[2] for k in keys if abs(k[3] - 19.00) < 0.05]
    med = float(np.median(main)) if main else 0.0
    keys = [(x, y, med if abs(dx - 19.00) < 0.05 else a) for (x, y, a, dx) in keys]
    line, polys = capline(keys)
    P = np.array([(k[0], k[1]) for k in keys])
    # pitch stats: nearest neighbour per key
    nn = []
    for i in range(len(P)):
        d = np.hypot(*(P - P[i]).T); d[i] = 99
        nn.append(d.min())
    out[side] = dict(n_keys=len(keys),
                     keys=[list(k[:3]) for k in keys],
                     cap_polys=polys,
                     other_holes=[list(o) for o in others],
                     capline={str(k): v for k, v in sorted(line.items())})
    ks = sorted(line)
    print(f"plate-{side}: {len(keys)} keys, angles "
          f"{sorted(set(round(k[2],1) for k in keys))}, NN pitch "
          f"{min(nn):.2f}..{max(nn):.2f}, other holes {len(others)}")
    print(f"  capline X {ks[0]}..{ks[-1]}, northernmost cap edge "
          f"{min(line.values()):.2f} at X {min(line, key=line.get)}")

json.dump(out, open(os.path.join(RT, "caps.json"), "w"), indent=1)
print("wrote caps.json")
