"""Issue #270 follow-up: tight J2-tab comparison figures.

PO feedback: at full-layout scale current/A/C look identical. These
figures crop a 45x45mm window centred on the J2 (left) tab so the
outline differences are unmissable.
Outputs: fig-zoom-compare.png (3 panels), fig-zoom-overlay.png.
Data: geometry.json + candidates.json (stage 1, unchanged).
"""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Polygon as MplPoly, Circle
from matplotlib.lines import Line2D

font_manager.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
plt.rcParams['font.family'] = 'Noto Sans CJK JP'

g = json.load(open('geometry.json'))
cand = json.load(open('candidates.json'))

rev8 = g['main_rev8_outline']
polyA = cand['polys']['A']
polyC = cand['polys']['C']
wingL = g['wings']['left']['outline']
padsJ2 = [pd['corners'] for pd in g['main_zif_pads']['J2']]

# --- crop: 45x45mm centred on the J2 tab (front y~34, base y~51) ---------
CX, CY, W = -26.0, 42.0, 45.0
XLIM = (CX - W / 2, CX + W / 2)
YLIM = (CY + W / 2, CY - W / 2)  # inverted: smaller y (north) on top
print('crop xlim', XLIM, 'ylim', YLIM)

# highlight target: outline point closest to the tab front corner zone
TX, TY = -23.5, 34.0


def front_point(poly):
    pts = [(p[0], p[1]) for p in poly if XLIM[0] < p[0] < XLIM[1]]
    return min(pts, key=lambda p: (p[0] - TX) ** 2 + (p[1] - TY) ** 2)


def base(ax):
    ax.add_patch(MplPoly(wingL, closed=True, facecolor='#2b6cb0', alpha=0.10,
                         edgecolor='#2b6cb0', lw=1.2, zorder=1))
    for c in padsJ2:
        ax.add_patch(MplPoly(c, closed=True, facecolor='#4a5568',
                             edgecolor='none', zorder=3))
    ax.annotate('Wing左の外形', xy=(XLIM[0] + 1.2, YLIM[1] + 2.8),
                fontsize=11, color='#2b6cb0', zorder=6)
    ax.annotate('J2パッド', xy=(-13.5, 43.5), fontsize=11, color='#4a5568',
                zorder=6, ha='left')
    ax.set_aspect('equal')
    ax.set_xlim(*XLIM); ax.set_ylim(*YLIM)
    ax.tick_params(labelsize=10)


def main_outline(ax, poly, color, lw=3.0, ls='-', zorder=4, fill=True):
    ax.add_patch(MplPoly(poly, closed=True,
                         facecolor='#e53e3e' if fill else 'none',
                         alpha=0.10 if fill else 1.0,
                         edgecolor=color, lw=lw, linestyle=ls, zorder=zorder))


# --- fig 1: three panels --------------------------------------------------
panels = [
    ('現行 Rev.8', rev8, '#333333',
     '現行：四角いタブ\n（角は直角、付け根も直角）'),
    ('候補A（推奨）', polyA, '#1a56db',
     'A：前面の角 R2.0\n＋付け根フィレット R2.0'),
    ('候補C', polyC, '#dd6b20',
     'C：左右対称の台形\n（壁が斜め・左右で同形）'),
]
fig, axes = plt.subplots(1, 3, figsize=(15.5, 6.2))
for ax, (title, poly, col, note) in zip(axes, panels):
    base(ax)
    main_outline(ax, poly, col)
    fp = front_point(poly)
    ax.add_patch(Circle(fp, 5.0, fill=False, edgecolor=col, lw=1.6,
                        linestyle=(0, (3, 2)), zorder=6))
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.text(0.5, 0.03, note, transform=ax.transAxes, ha='center', va='bottom',
            fontsize=12.5, linespacing=1.5,
            bbox=dict(boxstyle='round,pad=0.45', facecolor='white',
                      edgecolor=col, alpha=0.95), zorder=7)
fig.suptitle('J2タブ部の拡大比較（同縮尺・45mm四方、丸囲み＝タブ前面の角）',
             fontsize=16.5, fontweight='bold')
fig.tight_layout(rect=(0, 0, 1, 0.94))
fig.savefig('fig-zoom-compare.png', dpi=130)
plt.close(fig)
print('saved fig-zoom-compare.png')

# --- fig 2: overlay --------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.6, 7.4))
base(ax)
ax.add_patch(MplPoly(polyC, closed=True, facecolor='none', edgecolor='#dd6b20',
                     lw=2.8, zorder=4))
ax.add_patch(MplPoly(polyA, closed=True, facecolor='none', edgecolor='#1a56db',
                     lw=2.8, zorder=5))
main_outline(ax, rev8, '#444444', lw=2.4, ls=(0, (5, 3)), zorder=6, fill=False)
ax.legend(handles=[
    Line2D([], [], color='#666666', lw=2.4, linestyle=(0, (5, 3)), label='現行 Rev.8'),
    Line2D([], [], color='#1a56db', lw=2.8, label='候補A：角R2.0＋付け根フィレット'),
    Line2D([], [], color='#dd6b20', lw=2.8, label='候補C：左右対称の台形'),
], loc='lower left', fontsize=11.5, framealpha=0.95)
ax.set_title('J2タブ部の重ね合わせ（3案の外形差）', fontsize=16, fontweight='bold')
fig.tight_layout()
fig.savefig('fig-zoom-overlay.png', dpi=130)
plt.close(fig)
print('saved fig-zoom-overlay.png')
