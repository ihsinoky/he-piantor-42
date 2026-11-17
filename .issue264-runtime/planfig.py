import sys, math
def path_V(s1_dy=0.0):
    din = (0.04643, 0.99892); s1 = (14.08, 24.4 + s1_dy); S2X = 13.00
    return [(27.0, -38.5, 2.95), (25.2, -15.0, 2.95), (11.37, -22.0, 2.95),
            (11.44, -19.0, 2.95), (12.29, -15.0, 4.93), (12.48, -11.0, 6.90),
            (s1[0]-3*din[0], s1[1]-3*din[1], 6.90), (s1[0], s1[1], 7.06),
            (s1[0]-3*0.0464, s1[1]-3*0.9989, 7.22),
            (S2X+3*0.0464, 0.43+3*0.9989, 7.22), (S2X, 0.43, 7.38),
            (S2X+3*din[0], 0.43+3*din[1], 7.54), (14.41, 30.60, 7.54),
            (14.41+3*0.6474, 30.60+3*0.7622, 7.22), (20.92, 38.24, 6.90),
            (22.6, 40.0, 6.90)]
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
import numpy as np

V = path_V(0.0)
xs = [p[0] for p in V]; ys = [p[1] for p in V]
fig, ax = plt.subplots(figsize=(7.2, 8.6))
# strip width band
for a, b in zip(V, V[1:]):
    ax.plot([a[0], b[0]], [a[1], b[1]], color='#7fb2e5', lw=13, solid_capstyle='butt', alpha=0.55, zorder=1)
ax.plot(xs, ys, 'o-', color='#0b4f9e', lw=1.6, ms=4, zorder=3)
# ZIF envelopes
ax.add_patch(Rectangle((21.5, -41.0), 11, 7, fill=False, ec='#c0392b', lw=1.6))
ax.add_patch(Rectangle((17.8, 37.3), 11, 7, fill=False, ec='#c0392b', lw=1.6))
labels = {0: 'T0 Wing tail\n(in ZIF)', 1: 'F_A fold 112.5°', 2: 'F_B fold 119.6°',
          7: 'F_S1 fold 180°\n(slider, absorbs length)', 10: 'F_S2 fold 180°',
          12: 'F_V7 fold 37.7°', 15: 'T1 Main tail\n(in ZIF)'}
for i, t in labels.items():
    ax.annotate(t, (xs[i], ys[i]), textcoords='offset points', xytext=(10, 6), fontsize=8.5, color='#0b4f9e')
ax.annotate('Wing ZIF (underside)\n(27.0, -37.5)', (27, -37.5), textcoords='offset points', xytext=(-118, -4), fontsize=8.5, color='#c0392b')
ax.annotate('Main ZIF (top, yaw -43°)\n(23.3, 40.8)', (23.3, 40.8), textcoords='offset points', xytext=(-128, 2), fontsize=8.5, color='#c0392b')
ax.annotate('S-pair stack zone\n(3 layers, legs at z 6.90/7.22/7.54)', (13.4, 12), textcoords='offset points', xytext=(16, -30), fontsize=8.5, color='#555555')
ax.set_xlabel('case X (mm)'); ax.set_ylabel('case Y (mm)')
ax.set_title('Issue 264 — folded stock FFC plan view (RIGHT side; left is the mirror)\nMolex 152660149, 152 mm, Type A — 5 folds, contact face UP at Wing → DOWN at Main', fontsize=10)
ax.set_aspect('equal'); ax.grid(alpha=0.25)
ax.set_xlim(0, 42); ax.set_ylim(-48, 50)
plt.tight_layout()
out = '/home/hatch/workspace/projects/he-piantor-stockffc/hardware/case/issue-264-stockffc/plan-view.png'
plt.savefig(out, dpi=150)
print('saved', out)
# also dump the vertex table as CSV for the report
import csv
names = ['T0','A (F_A)','B (F_B)','flat','climb-mid','climb-top','pre-S1','S1 (F_S1)','post-S1','pre-S2','S2 (F_S2)','post-S2','V7 (F_V7)','exit','mouth','T1']
with open('/home/hatch/workspace/projects/he-piantor-stockffc/hardware/case/issue-264-stockffc/path-vertices.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['point', 'x', 'y', 'z_centreline'])
    for n, p in zip(names, V): w.writerow([n, p[0], p[1], p[2]])
print('csv saved')
