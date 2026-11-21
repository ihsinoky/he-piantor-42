"""Per-part north boundary curves + strip north-face Z profile, from STLs."""
import numpy as np, struct, os

OUT = os.path.expanduser("~/workspace/projects/he-piantor-case296b/hardware/case/issue-296-wireless")

def load_stl(path):
    with open(path,'rb') as f: data = f.read()
    n = struct.unpack('<I', data[80:84])[0]
    dt = np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')])
    return np.frombuffer(data[84:84+n*50], dtype=dt)['v'].reshape(-1,3)

def north_curve(V, x0, x1, step=2.0):
    out = []
    x = x0
    while x < x1:
        m = (V[:,0] >= x) & (V[:,0] < x+step)
        out.append((x+step/2, float(V[m,1].min()) if m.any() else None))
        x += step
    return out

for part in ["strip-right","tray-right"]:
    V = load_stl(f"{OUT}/{part}.stl")
    print(f"\n== {part}: Ymin per 5mm X-bin, X 30..130 ==")
    for xc, y in north_curve(V, 30, 130, 5.0):
        if y is not None:
            print(f"  X {xc:6.1f}  Ymin {y:8.2f}  dev {y+64.37:6.2f}")

# strip north-face profile: min Y per (X station, Z bin)
V = load_stl(f"{OUT}/strip-right.stl")
print("\n== strip-right north face: Ymin per Z-bin at X stations ==")
for xst in [40, 60, 80, 100]:
    m = (V[:,0] >= xst-2.5) & (V[:,0] < xst+2.5)
    row = []
    for z0 in range(11, 22, 2):
        mz = m & (V[:,2] >= z0) & (V[:,2] < z0+2)
        row.append(f"Z{z0}: {V[mz,1].min():7.2f}" if mz.any() else f"Z{z0}:   --  ")
    print(f"  X~{xst}: " + "  ".join(row))

# tray north face profile (below the strip), X stations
V = load_stl(f"{OUT}/tray-right.stl")
print("\n== tray-right north face: Ymin per Z-bin at X stations ==")
for xst in [40, 60, 80, 100]:
    m = (V[:,0] >= xst-2.5) & (V[:,0] < xst+2.5)
    row = []
    for z0 in [-2, 1, 4, 7, 10]:
        mz = m & (V[:,2] >= z0) & (V[:,2] < z0+3)
        row.append(f"Z{z0}: {V[mz,1].min():7.2f}" if mz.any() else f"Z{z0}:   --  ")
    print(f"  X~{xst}: " + "  ".join(row))
