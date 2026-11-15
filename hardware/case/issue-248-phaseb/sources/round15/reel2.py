"""Round 15 slack reel: round 14 accounting, per-side centres.

Round 14 put both sides' reels on one shared axis C=(0,5); the mirror
construction then gives, at every Z level of the ladder, a left arc
and a right arc with the SAME radius (left pin 15-p pairs with right
pin p, design index equal), and the two 270 deg sweeps overlap on the
north and south bands - the mirrored reels cannot coexist. Round 15
therefore uses per-side centres C=(+/-13, 5); entry/exit directions,
270 deg sweep, Z ladder (4.6+1.12i) and the slack accounting of
reel_build.py are unchanged.
"""
import numpy as np
C = np.array([13.0, 5.0])
U = np.array([np.cos(np.radians(-45.0)), np.sin(np.radians(-45.0))])
def rot(v, deg):
    t = np.radians(deg); c, s = np.cos(t), np.sin(t)
    return np.array([c * v[0] - s * v[1], s * v[0] + c * v[1]])
W = rot(U, -270.0)
TMID = rot(U, -135.0)
def z_of(i): return 4.6 + 1.12 * i
def entry(i, R=8.0):
    p = C + R * U; return np.array([p[0], p[1], z_of(i)])
def exitp(i, R=8.0):
    p = C + R * W; return np.array([p[0], p[1], z_of(i)])
def midp(i, R=8.0):
    p = C + R * TMID; return np.array([p[0], p[1], z_of(i)])
T_ENTRY = np.array([-0.70710678, -0.70710678, 0.0])   # arc entry tangent (CW at -45)
T_EXIT = np.array([0.70710678, -0.70710678, 0.0])     # arc exit tangent (CW at 45)
