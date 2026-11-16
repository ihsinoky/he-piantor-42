"""Stage-0 dimensioned sketch (top view, left Wing, 17 mm) from measured rays."""
import json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

d = json.load(open('/home/hatch/workspace/projects/he-piantor-north/.issue253-runtime/stage0_out.json'))
w = json.load(open('/home/hatch/workspace/projects/he-piantor-north/.issue253-runtime/stage0_wall.json'))
rows = [r for r in d['17mm']['left']['z7.95'] if -105 <= r[0] <= -10]
xs = np.array([r[0] for r in rows]); edge = np.array([r[1] for r in rows])
wall = edge - 0.502
wr = w['17left']
ox = np.array([r['x'] for r in wr]); outer = np.array([r['tray795'][0][0] for r in wr])

fig, ax = plt.subplots(figsize=(9, 5.2))
ax.fill_between(xs, edge, wall, color='0.75', label='pocket clearance 0.50')
ax.fill_between(ox, [r['tray795'][0][1] for r in wr], outer, color='0.45',
                label='tray north rim land (measured 5.0-9.0 thick)')
ax.plot(xs, edge, 'k-', lw=1.6, label='Wing Rev.4 PCB north edge (measured)')
ax.plot(ox, outer, 'k--', lw=1.2, label='case outer silhouette D-037 (fixed)')
ext = np.array([3.86, 4.80, 5.84, 6.99])
ax.fill_between(ox, [r['tray795'][0][1] for r in wr],
                [r['tray795'][0][1] for r in wr] - ext, color='tab:red', alpha=0.55,
                label='max extension zone (keeps >=2.0 land)')
ax.annotate('J_WING tab zone\nX -38..-16', xy=(-27, -47), xytext=(-95, -30),
            arrowprops=dict(arrowstyle='->'), fontsize=9)
ax.annotate('extension limit at outer tab end:\n3.86 mm (17 mm) / 3.01 mm (16 mm)',
            xy=(-40, -53), xytext=(-108, -68), arrowprops=dict(arrowstyle='->'), fontsize=9)
ax.set_xlabel('assembly X (mm)'); ax.set_ylabel('assembly Y (mm), north = -Y')
ax.set_title('Issue 253 Stage 0 - north free space, left Wing, 17 mm pitch, PCB band Z 7.35-8.55')
ax.legend(fontsize=8, loc='lower right'); ax.set_aspect('equal'); ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig('/home/hatch/workspace/projects/he-piantor-north/.issue253-runtime/stage0-sketch-left17.png', dpi=150)
print('saved')
