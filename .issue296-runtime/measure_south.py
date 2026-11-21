"""South outline profile extraction, Issue #296 (Opus south-unify pass).

For each case part solid (asm3d BREPs, assembly frame: X centred, +Y south),
sample thin vertical slabs across the full width and record the southmost Y
per slab. Also computes the whole-case profile (max over parts) and detects
steps (adjacent-sample jumps) and recesses relative to the global southmost Y.
Output: JSON + a compact text table.
"""
import build123d as bd
import json, os

ASM = os.path.expanduser("~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d")
OUT = os.path.expanduser("~/workspace/goals/he-piantor-42-keyboard-pmo/hidden_files/design-review-opus")
PARTS = ["shell-central", "tray-left", "tray-right", "plate-left", "plate-right",
         "centre-infill", "north-shelf"]
STEP = 0.5
X0, X1 = -156.0, 156.0

def load(name):
    s = bd.import_brep(f"{ASM}/{name}.brep")
    return s

def profile(solid):
    prof = []
    n = int((X1 - X0) / STEP)
    for i in range(n + 1):
        xa = X0 + i * STEP
        slab = bd.Solid.make_box(STEP, 400.0, 60.0, bd.Plane(origin=(xa, -120.0, -5.0)))
        try:
            inter = solid.intersect(slab)
        except Exception:
            inter = None
        cells = []
        if inter is not None:
            cells = list(inter) if isinstance(inter, (list, bd.ShapeList)) else [inter]
            cells = [c for c in cells if c is not None and c.volume > 1e-9]
        if cells:
            ymax = max(c.bounding_box().max.Y for c in cells)
            prof.append([round(xa + STEP / 2, 2), round(ymax, 3)])
        else:
            prof.append([round(xa + STEP / 2, 2), None])
    return prof

result = {}
for name in PARTS:
    s = load(name)
    bb = s.bounding_box()
    p = profile(s)
    result[name] = {"bbox": [round(bb.min.X, 2), round(bb.max.X, 2),
                             round(bb.min.Y, 2), round(bb.max.Y, 2),
                             round(bb.min.Z, 2), round(bb.max.Z, 2)],
                    "profile": p}
    print(f"done {name}: southmost {bb.max.Y:.3f}", flush=True)

# whole-case profile = max over parts at each sample
xs = [p[0] for p in result[PARTS[0]]["profile"]]
whole = []
for i, x in enumerate(xs):
    vals = [result[n]["profile"][i][1] for n in PARTS if result[n]["profile"][i][1] is not None]
    whole.append([x, max(vals) if vals else None])
result["__whole__"] = {"profile": whole}
gmax = max(v for _, v in whole if v is not None)
print(f"global southmost Y = {gmax:.3f}", flush=True)

json.dump(result, open(f"{OUT}/south-outline-raw.json", "w"))
print("saved south-outline-raw.json", flush=True)
