"""Round 15 rise skeleton (route-envelope adjustment, unfreeze step 1
class). Round 14's rise line (Y=-7, round-9 zf ladder) is blocked for
the eastern strands: at (28.85,-7) and (27.6,-7) the vertical window
has max min-body distance 0.0 over Z in [7.6,11.6] (switch envelope
R0_C5 sits on the Wing PCB with no wire-sized gap), and strands 1-2's
rise tops are INSIDE the envelope (exact signed distance -0.563 /
-0.975 at 17/16 mm). Exact-oracle scans (RT15/rise_y_scan2.json) give
per-strand rise lines with >= 0.82 mm point clearance at both pitches:
  strands 1-9:  Y=-11, Z=10.3  (clearance 1.67-1.75)
  strand 10:    Y=-12, Z=9.9   (1.51)
  strands 11-14: Y=-13, Z=8.2  (0.82-1.35)
Corridor point unchanged (fx, -18, 5.1); the climb segment runs
north-up at constant X = fx from Y -18 to the new rise Y.
"""
import numpy as np
import design_r14 as dz

RISE_YZ = {0: (-11., 10.3), 1: (-11., 10.3), 2: (-11., 10.3), 3: (-11., 10.3),
           4: (-11., 10.3), 5: (-11., 10.3), 6: (-11., 10.3), 7: (-11., 10.3),
           8: (-11., 10.3), 9: (-12., 9.9), 10: (-13., 8.2), 11: (-13., 8.2),
           12: (-13., 8.2), 13: (-13., 8.2)}

def corridor(i):
    # unchanged from round 14: (fx, -18, 5.1); the climb segment runs
    # from here north-up at constant X = fx to the new rise top.
    # (Computed directly, not via dz.corridor, so callers may safely
    # monkeypatch design_r14.corridor with this function.)
    return np.array([dz.fx_of(i), -18.0, 5.1])

def rise_top(i):
    y, z = RISE_YZ[i]
    return np.array([dz.fx_of(i), y, z])
