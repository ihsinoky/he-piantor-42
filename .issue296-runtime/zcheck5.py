import sys, json
sys.path.insert(0, "/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr/lib/python3/dist-packages")
import pcbnew, numpy as np

B = "/home/hatch/workspace/projects/he-piantor-wwing-review/hardware/kicad/qualification/issue-299-wwing/17R/wwing-17r.kicad_pcb"
b = pcbnew.LoadBoard(B)
pts = []
for d in b.GetDrawings():
    if d.GetLayer() == pcbnew.Edge_Cuts:
        pts.append((d.GetStart().x/1e6, d.GetStart().y/1e6))
        pts.append((d.GetEnd().x/1e6, d.GetEnd().y/1e6))
bp = np.array(sorted(set(pts)))
asm_raw = json.load(open("/home/hatch/workspace/projects/he-piantor-case296b/.issue296-runtime/wing17r-outline-asm.json"))
print("asm item sample:", asm_raw[0])
pts_a = []
for it in asm_raw:
    for p in it[1:]:
        if isinstance(p, list) and len(p) == 2 and isinstance(p[0], (int, float)):
            pts_a.append(tuple(p))
ap = np.array(sorted(set(pts_a)))
print("board pts", bp.shape, "asm pts", ap.shape)
# Kabsch: match by nearest neighbour iteration (sets should be identical up to rigid transform)
def kabsch(P, Q):
    Pc, Qc = P.mean(0), Q.mean(0)
    H = (P-Pc).T @ (Q-Qc)
    U, S, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    D = np.diag([1, d])
    R = Vt.T @ D @ U.T
    t = Qc - R @ Pc
    return R, t
# initial pairing by sorted order may mismatch; use ICP-lite: pair each board pt to nearest asm pt after rough alignment by centroids+bbox
th = np.radians(-29.996)
R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
t = ap.mean(0) - R @ bp.mean(0)
for _ in range(80):
    P2 = (R @ bp.T).T + t
    # nearest asm point for each
    d2 = ((P2[:,None,:] - ap[None,:,:])**2).sum(-1)
    Q = ap[d2.argmin(1)]
    R, t = kabsch(bp, Q)
P2 = (R @ bp.T).T + t
res = np.sqrt(((P2 - Q)**2).sum(-1))
print("fit: angle %.4f deg, t=(%.3f, %.3f), residual max %.4f mean %.4f" % (np.degrees(np.arctan2(R[1,0], R[0,0])), t[0], t[1], res.max(), res.mean()))
np.save("/home/hatch/workspace/projects/he-piantor-case296b/.issue296-runtime/zcheck_R.npy", R)
np.save("/home/hatch/workspace/projects/he-piantor-case296b/.issue296-runtime/zcheck_t.npy", t)
def to_asm(p): return R @ np.array(p) + t
def to_board(p): return R.T @ (np.array(p) - t)
# J_WING in board + asm
for fp in b.GetFootprints():
    if fp.GetReference() == "J_WING":
        c = fp.GetPosition()
        print("J_WING board centre (%.3f, %.3f) -> asm (%.3f, %.3f), layer %s, rot %.1f" % (c.x/1e6, c.y/1e6, *to_asm((c.x/1e6, c.y/1e6)), "B" if fp.GetLayer()==pcbnew.B_Cu else "F", fp.GetOrientationDegrees()))
# overlap rect corners -> board coords
rect = [(22.50,-45.0),(26.25,-45.0),(26.25,-8.7),(22.50,-8.7)]
print("overlap rect in board coords:", [tuple(np.round(to_board(p),2)) for p in rect])
json.dump({"R": R.tolist(), "t": t.tolist()}, open("/home/hatch/workspace/projects/he-piantor-case296b/.issue296-runtime/zcheck_transform.json","w"))
