"""PO-facing 2D views of the wireless Main, rendered from the FINISHED
tree board (official ISP1807 footprint, module field routed under the
D-057 rule exception)."""
import json, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrow
import matplotlib.font_manager as fm

for f in fm.findSystemFonts():
    if 'NotoSansCJK' in f:
        fm.fontManager.addfont(f)
plt.rcParams['font.family'] = 'Noto Sans CJK JP'
D = json.load(open('/home/hatch/workspace/projects/he-piantor-wmain-fix/.issue292-runtime/board_dump_final.json'))
OUT = '/home/hatch/workspace/goals/he-piantor-42-keyboard-pmo/files/'
FPS = {f['ref']: f for f in D['fps']}

# --- board outline as a clip path: annotation overlays must never draw
# outside the board (edge-fix round requirement) ---
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch as MplPathPatch

def outline_path():
    segs = [((x1, y1), (x2, y2)) for (x1, y1, x2, y2) in D['edges']]
    pts = [segs[0][0], segs[0][1]]
    used = {0}
    while len(used) < len(segs):
        last = pts[-1]
        for i, (a, b) in enumerate(segs):
            if i in used: continue
            if abs(a[0] - last[0]) < 1e-6 and abs(a[1] - last[1]) < 1e-6:
                pts.append(b); used.add(i); break
            if abs(b[0] - last[0]) < 1e-6 and abs(b[1] - last[1]) < 1e-6:
                pts.append(a); used.add(i); break
        else:
            break
    return MplPath(pts, closed=True)

OUTLINE = outline_path()

def clip_to_board(ax, patch):
    cp = MplPathPatch(OUTLINE, fill=False, edgecolor='none', lw=0)
    ax.add_patch(cp)
    patch.set_clip_path(cp)
    return patch

def base(ax):
    for t in D['tracks']:
        if t['layer'] == 'F':
            ax.plot([t['x1'], t['x2']], [t['y1'], t['y2']], color='#9db8d6', lw=max(0.5, t['w'] * 2.2), zorder=0, solid_capstyle='round')
    for v in D['vias']:
        ax.add_patch(Circle((v['x'], v['y']), v['d'] / 2, facecolor='#9db8d6', edgecolor='none', zorder=0))
    for (x1, y1, x2, y2) in D['edges']:
        ax.plot([x1, x2], [y1, y2], color='#333333', lw=1.6)
    for f in D['fps']:
        for pd in f['pads']:
            ax.add_patch(Rectangle((pd['x'] - pd['sx'] / 2, pd['y'] - pd['sy'] / 2), pd['sx'], pd['sy'],
                                   facecolor='#c9ced6', edgecolor='none', zorder=1))

def setup(ax, xlim, ylim):
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    ax.invert_yaxis(); ax.set_aspect('equal'); ax.axis('off')

# ---------- full top view ----------
fig, ax = plt.subplots(figsize=(11.5, 10))
base(ax)
u1 = FPS['U1']
for pd in u1['pads']:
    ax.add_patch(Rectangle((pd['x'] - pd['sx'] / 2, pd['y'] - pd['sy'] / 2), pd['sx'], pd['sy'],
                           facecolor='#e07b39', edgecolor='#8a4b12', lw=0.4, zorder=3))
ax.add_patch(Rectangle((70.7, 120.85), 8.8, 8.0, fill=False, edgecolor='#8a4b12', lw=1.2, zorder=4))
clip_to_board(ax, ax.add_patch(Rectangle((70.3, 128.9), 9.6, 9.0, facecolor='#3f7fbf', alpha=0.25, edgecolor='#3f7fbf', lw=1.2, zorder=2)))
clip_to_board(ax, ax.add_patch(Circle((100, 118), 20, fill=False, edgecolor='#7a4fbf', lw=1.4, zorder=4)))
clip_to_board(ax, ax.add_patch(Rectangle((64.1, 131.0), 71.8, 6.9, facecolor='#4f9e57', alpha=0.13, edgecolor='none', zorder=0)))
def lab(x, y, s, dx=0, dy=0, color='#111111', size=10.5, ha='left'):
    ax.annotate(s, (x, y), (x + dx, y + dy), fontsize=size, color=color, ha=ha,
                arrowprops=dict(arrowstyle='-', color=color, lw=0.7))
lab(75.1, 124.85, 'U1 ISP1807-LR モジュール\n（公式フットプリント検証済）', dx=-24, dy=-9, size=11)
lab(75.1, 133.4, 'アンテナ・キープアウト\n（全層・金属禁止）', dx=-13, dy=6.5, color='#2c5f8a')
lab(100, 118, 'トラックパッド Ø40\nキープアウト', dx=13, dy=-14, color='#5b3a8a')
lab(75.7, 111.8, 'J2 FH12（左Wing）', dx=-16, dy=-6)
lab(124.3, 111.8, 'J3 FH12（右Wing）', dx=3, dy=-6)
lab(100, 90, 'J4 EZmate（USB子基板へ）', dx=3, dy=-3)
lab(89, 97, 'U2 TPS63070 電源部', dx=-24, dy=3)
lab(113.5, 136.2, 'JSWD（SWDパッド）', dx=2, dy=3)
lab(124, 134.5, 'JBATT（電池）', dx=2, dy=-4)
lab(100, 134.5, '南側バンド', dx=-6, dy=4.5, color='#2e6b34')
ax.plot([66, 76], [140.5, 140.5], color='#111111', lw=2.5)
ax.text(71, 142.3, '10 mm', ha='center', fontsize=10)
ax.text(64, 72.5, '無線Main（Issue #292）上面図 — エッジ修正済みツリー基板から描画\n'
                  '外形はRev.10と同一／銅の外形はみ出し0件（包含ゲート合格、REPORT.md 偏差13）',
        fontsize=11.5, va='top')
setup(ax, (60, 140), (70, 144))
fig.savefig(OUT + 'wmain-2d-topview.png', dpi=200, bbox_inches='tight')
plt.close(fig)

# ---------- module zoom ----------
fig, ax = plt.subplots(figsize=(9.5, 9.5))
base(ax)
for pd in u1['pads']:
    ax.add_patch(Rectangle((pd['x'] - pd['sx'] / 2, pd['y'] - pd['sy'] / 2), pd['sx'], pd['sy'],
                           facecolor='#e07b39', edgecolor='#8a4b12', lw=0.5, zorder=3))
    if pd['n'] in ('1', '20', '22', '26', '12'):
        ax.text(pd['x'], pd['y'], pd['n'], fontsize=7.5, ha='center', va='center', zorder=5)
for t in D['tracks']:
    if 63 < t['x1'] < 91 and 114 < t['y1'] < 140:
        col = {'F': '#c2452d', 'I2': '#2d7fc2', 'B': '#37a05a'}.get(t['layer'], '#888888')
        ax.plot([t['x1'], t['x2']], [t['y1'], t['y2']], color=col, lw=max(0.6, t['w'] * 2.6), zorder=2, solid_capstyle='round')
for v in D['vias']:
    if 63 < v['x'] < 91 and 114 < v['y'] < 140:
        ax.add_patch(Circle((v['x'], v['y']), v['d'] / 2, facecolor='#555555', edgecolor='none', zorder=2))
ax.add_patch(Rectangle((70.7, 120.85), 8.8, 8.0, fill=False, edgecolor='#8a4b12', lw=1.4, zorder=4))
ax.add_patch(Rectangle((69.3, 119.05), 11.6, 9.85, fill=False, edgecolor='#d62728', lw=2.2, linestyle=(0, (5, 2)), zorder=5))
clip_to_board(ax, ax.add_patch(Rectangle((70.3, 128.9), 9.6, 9.0, facecolor='#3f7fbf', alpha=0.25, edgecolor='#3f7fbf', lw=1.2, zorder=2)))
ax.plot([71.6], [121.35], marker='o', color='#b02020', markersize=7, zorder=6)
def lab2(x, y, s, dx=0, dy=0, color='#111111', size=10.5):
    ax.annotate(s, (x, y), (x + dx, y + dy), fontsize=size, color=color,
                arrowprops=dict(arrowstyle='-', color=color, lw=0.7))
lab2(71.6, 121.35, 'ピン1（北西）', dx=-6.5, dy=-1.5, color='#b02020')
lab2(75.1, 128.6, '南端列＝NCパッド 65–78（公式CADで追加）', dx=-4, dy=3.2)
lab2(76.7, 124.65, 'ピン20/22 アンテナ端子', dx=4.5, dy=0.5)
lab2(75.1, 133.4, 'アンテナ・キープアウト', dx=-3, dy=3.4, color='#2c5f8a')
lab2(75.1, 117.5, 'モジュール拡大 — 公式フットプリント＋エッジ修正済\n赤破線＝D-057ルールエリア MODULE_FIELD_FINE（11.6×9.85mm）\nこの内側のみ 0.05mm級（実測最小：線幅0.050／間隔0.041・偏差13に記録）', dx=-9, dy=-2.5)
ax.plot([66, 71], [139.5, 139.5], color='#111111', lw=2.5)
ax.text(68.5, 140.8, '5 mm', ha='center', fontsize=10)
setup(ax, (63.5, 90), (115, 142))
fig.savefig(OUT + 'wmain-2d-zoom-module.png', dpi=200, bbox_inches='tight')
plt.close(fig)

# ---------- service zoom (south band: JSWD + JBATT) ----------
fig, ax = plt.subplots(figsize=(10.5, 6.5))
base(ax)
clip_to_board(ax, ax.add_patch(Rectangle((64.1, 131.0), 71.8, 6.9, facecolor='#4f9e57', alpha=0.13, edgecolor='none', zorder=0)))
for ref in ('JSWD', 'JBATT', 'J3'):
    f = FPS[ref]
    for pd in f['pads']:
        ax.add_patch(Rectangle((pd['x'] - pd['sx'] / 2, pd['y'] - pd['sy'] / 2), pd['sx'], pd['sy'],
                               facecolor='#e07b39', edgecolor='#8a4b12', lw=0.4, zorder=3))
def lab3(x, y, s, dx=0, dy=0, color='#111111', size=11):
    ax.annotate(s, (x, y), (x + dx, y + dy), fontsize=size, color=color,
                arrowprops=dict(arrowstyle='-', color=color, lw=0.7))
lab3(113.5, 136.2, 'JSWD SWDパッド\n（nRF52840 DKで書込）', dx=-9, dy=-4.5)
lab3(124, 134.5, 'JBATT 電池コネクタ\n（JST GH）', dx=1, dy=-4.5)
lab3(124.3, 111.8 + 14, 'J3 FH12（右Wing）南端', dx=2, dy=1)
lab3(100, 134.5, '南側バンド（直線化した外形側）', dx=-8, dy=3.5, color='#2e6b34')
ax.plot([97, 107], [141.5, 141.5], color='#111111', lw=2.5)
ax.text(102, 143, '10 mm', ha='center', fontsize=10)
ax.text(95, 123.5, 'サービス面拡大 — 南側バンド（SWD／電池）', fontsize=11.5, va='top')
setup(ax, (94, 138), (122, 144.5))
fig.savefig(OUT + 'wmain-2d-zoom-service.png', dpi=200, bbox_inches='tight')
plt.close(fig)
print('rendered 3 PNGs')
