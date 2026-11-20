import pcbnew as p, json, math
import numpy as np
def mm(v): return v/1e6
b = p.LoadBoard("/home/hatch/workspace/projects/he-piantor-wmain2/hardware/kicad/qualification/issue-270-wing-rev6/wing-rev6-17mm-right/main.kicad_pcb")
fps = {}
for fp in b.GetFootprints():
    fps[fp.GetReference()] = (mm(fp.GetPosition().x), mm(fp.GetPosition().y))
idx = json.load(open("/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17/index.json"))
pairs = []
for i, e in enumerate(idx):
    n = e["name"]
    if n.startswith("underside-right-"):
        ref = n[len("underside-right-"):]
        if ref in fps:
            (x0,y0,z0),(x1,y1,z1) = e["bounds"]
            pairs.append((ref, fps[ref], ((x0+x1)/2, (y0+y1)/2)))
print("anchor pairs:", len(pairs))
P = np.array([q[1] for q in pairs]); Q = np.array([q[2] for q in pairs])
def fit(P, Q, mirror=False):
    Pm = P.copy(); 
    if mirror: Pm[:,0] = -Pm[:,0]
    pc, qc = Pm.mean(0), Q.mean(0)
    X = Pm - pc; Y = Q - qc
    H = X.T @ Y
    U, S, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T
    if np.linalg.det(R) < 0: Vt[-1] *= -1; R = Vt.T @ U.T
    t = qc - R @ pc
    pred = (R @ Pm.T).T + t
    res = np.linalg.norm(pred - Q, axis=1)
    return R, t, res
for mirror in (False, True):
    R, t, res = fit(P, Q, mirror)
    ang = math.degrees(math.atan2(R[1,0], R[0,0]))
    print(f"mirror={mirror}: rot={ang:.3f} deg, t=({t[0]:.3f},{t[1]:.3f}), resid max={res.max():.3f} mean={res.mean():.3f}")
    if res.max() < 0.6:
        print("  per-anchor resid:", {q[0]: round(float(r),3) for q, r in zip(pairs, res) if r > 0.25})
        np.savez("/home/hatch/workspace/projects/he-piantor-wmain2/.issue292-runtime/wing-fit.npz", R=R, t=t, mirror=mirror)
        # J_WING in assembly frame
        jw = np.array(fps["J_WING"])
        if mirror: jw = np.array([-jw[0], jw[1]])
        print("  J_WING file", fps["J_WING"], "-> g17", tuple(round(v,2) for v in (R @ jw + t)))
