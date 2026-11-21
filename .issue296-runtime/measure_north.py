"""Measure the north boundary of the case assembly from the exported STLs.
For each part: Ymin per 1mm X-bin (vertex-based), plus overall Ymin span.
Assembly north boundary = min over parts. Also north-face profile samples:
for chosen X stations, min Y per 2mm Z-bin."""
import numpy as np, struct, os, json

OUT = os.path.expanduser("~/workspace/projects/he-piantor-case296b/hardware/case/issue-296-wireless")
parts = ["tray-left","tray-right","centre-infill","shell-central","strip-left",
         "strip-right","plate-left","plate-right","battery-cover","plunger-sw1","light-pipe-dled"]

def load_stl(path):
    with open(path,'rb') as f:
        data = f.read()
    n = struct.unpack('<I', data[80:84])[0]
    dt = np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')])
    arr = np.frombuffer(data[84:84+n*50], dtype=dt)
    return arr['v'].reshape(-1,3)

res = {}
asm_min = {}
for p in parts:
    V = load_stl(f"{OUT}/{p}.stl")
    res[p] = dict(ymin=float(V[:,1].min()), ymax=float(V[:,1].max()),
                  xmin=float(V[:,0].min()), xmax=float(V[:,0].max()),
                  zmin=float(V[:,2].min()), zmax=float(V[:,2].max()))
    xb = np.floor(V[:,0]).astype(int)
    for x, y in zip(xb, V[:,1]):
        k = int(x)
        if k not in asm_min or y < asm_min[k][0]:
            asm_min[k] = (float(y), p)

print("== per-part bbox (Y north extent) ==")
for p, r in res.items():
    print(f"{p:16s} X {r['xmin']:8.2f}..{r['xmax']:8.2f}  Ymin {r['ymin']:8.2f}  Z {r['zmin']:6.2f}..{r['zmax']:6.2f}")

xs = sorted(asm_min)
print("\n== assembly north boundary Y_north(X), 5mm samples ==")
for x in range(-155, 156, 5):
    vals = [asm_min[k] for k in xs if x <= k < x+5]
    if vals:
        y, p = min(vals)
        print(f"X {x:5d}..{x+5:5d}  Ymin {y:8.2f}  dev from -64.37: {y+64.37:7.2f}  ({p})")
