"""PO-facing 2D views of the wireless Main, rendered from the swapped
working board data (wmain-v28-fp: official ISP1807 footprint, module
field unrouted pending the PO fanout decision)."""
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
D = json.load(open('/home/hatch/workspace/projects/he-piantor-wmain/.issue292-runtime/board_dump_v28.json'))
OUT = '/home/hatch/workspace/goals/he-piantor-42-keyboard-pmo/files/'
FPS = {f['ref']: f for f in D['fps']}

def base(ax):
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
ax.add_patch(Rectangle((70.3, 128.9), 9.6, 9.0, facecolor='#3f7fbf', alpha=0.25, edgecolor='#3f7fbf', lw=1.2, zorder=2))
ax.add_patch(Circle((100, 118), 20, fill=False, edgecolor='#7a4fbf', lw=1.4, zorder=4))
ax.add_patch(Rectangle((64.1, 131.0), 71.8, 6.9, facecolor='#4f9e57', alpha=0.13, edgecolor='none', zorder=0))
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
ax.text(64, 72.5, '無線Main（Issue #292）上面図 — 公式フットプリント適用後の作業基板から描画\n'
                  '注意：モジュール周辺は未配線（ファンアウトに要PO判断： REPORT.md 偏差9）',
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
ax.add_patch(Rectangle((70.7, 120.85), 8.8, 8.0, fill=False, edgecolor='#8a4b12', lw=1.4, zorder=4))
ax.add_patch(Rectangle((70.3, 128.9), 9.6, 9.0, facecolor='#3f7fbf', alpha=0.25, edgecolor='#3f7fbf', lw=1.2, zorder=2))
ax.plot([71.6], [121.35], marker='o', color='#b02020', markersize=7, zorder=6)
def lab2(x, y, s, dx=0, dy=0, color='#111111', size=10.5):
    ax.annotate(s, (x, y), (x + dx, y + dy), fontsize=size, color=color,
                arrowprops=dict(arrowstyle='-', color=color, lw=0.7))
lab2(71.6, 121.35, 'ピン1（北西）', dx=-6.5, dy=-1.5, color='#b02020')
lab2(75.1, 128.6, '南端列＝NCパッド 65–78（公式CADで追加）', dx=-4, dy=3.2)
lab2(76.7, 124.65, 'ピン20/22 アンテナ端子', dx=4.5, dy=0.5)
lab2(75.1, 133.4, 'アンテナ・キープアウト', dx=-3, dy=3.4, color='#2c5f8a')
lab2(75.1, 117.5, 'モジュール拡大 — 公式フットプリント（78パッド）\n旧・派生フットプリントとは全パッド位置が異なる（一致0件）', dx=-9, dy=-2.5)
ax.plot([66, 71], [139.5, 139.5], color='#111111', lw=2.5)
ax.text(68.5, 140.8, '5 mm', ha='center', fontsize=10)
setup(ax, (63.5, 90), (115, 142))
fig.savefig(OUT + 'wmain-2d-zoom-module.png', dpi=200, bbox_inches='tight')
plt.close(fig)

# ---------- service zoom (south band: JSWD + JBATT) ----------
fig, ax = plt.subplots(figsize=(10.5, 6.5))
base(ax)
ax.add_patch(Rectangle((64.1, 131.0), 71.8, 6.9, facecolor='#4f9e57', alpha=0.13, edgecolor='none', zorder=0))
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
