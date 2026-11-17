"""Issue #270 stage 2a figures (system python3 + matplotlib).
fig-s2a-layout.png: full flat layout, new outlines bold, current dashed.
fig-s2a-zoom-j2.png / fig-s2a-zoom-j3.png: tight seam zooms with
panels [current pair | new pair | overlay]."""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Polygon as MplPoly

font_manager.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
plt.rcParams['font.family'] = 'Noto Sans CJK JP'

g = json.load(open('geometry.json'))
s2a = json.load(open('stage2a.json'))
w2a = json.load(open('wing2a.json'))
sil = json.load(open('case_geometry.json'))['silhouette_parts']
rev8 = g['main_rev8_outline']
main_new = s2a['polys']['main']
pads = []
for ref, lst in g['main_zif_pads'].items():
    for pd in lst:
        pads.append(pd['corners'])

FULL = dict(xlim=(-152, 152), ylim=(88, -72))


def wing_cur(side):
    return g['wings'][side]['outline']


def wing_new(side):
    return s2a['polys'][f'17mm-{side}']


# ---------------- full layout ----------------
fig, ax = plt.subplots(figsize=(13.5, 7.2))
for part in sil:
    ax.add_patch(MplPoly(part, closed=True, facecolor='#e8e8e8', edgecolor='#aaaaaa', lw=0.8, zorder=0))
for side, col in (('left', '#2b6cb0'), ('right', '#c05621')):
    ax.add_patch(MplPoly(wing_cur(side), closed=True, facecolor='none', edgecolor='#999999',
                         lw=0.9, linestyle=(0, (4, 3)), zorder=1))
    wn = wing_new(side)
    ax.add_patch(MplPoly(wn, closed=True, facecolor=col, alpha=0.10,
                         edgecolor='none', zorder=2))
    ax.plot([c[0] for c in wn] + [wn[0][0]], [c[1] for c in wn] + [wn[0][1]],
            color=col, lw=1.3, zorder=2.5)
    kx = [k[0] for k in g['wings'][side]['keys']]
    ky = [k[1] for k in g['wings'][side]['keys']]
    ax.plot(kx, ky, '.', color=col, ms=4, zorder=3)
ax.add_patch(MplPoly(rev8, closed=True, facecolor='none', edgecolor='#999999',
                     lw=0.9, linestyle=(0, (4, 3)), zorder=3))
ax.add_patch(MplPoly(main_new, closed=True, facecolor='#e53e3e', alpha=0.13,
                     edgecolor='none', zorder=4))
ax.plot([c[0] for c in main_new] + [main_new[0][0]], [c[1] for c in main_new] + [main_new[0][1]],
        color='#c53030', lw=1.6, zorder=4.5)
for c in pads:
    ax.add_patch(MplPoly(c, closed=True, facecolor='#4a5568', edgecolor='none', zorder=5))
ax.set_aspect('equal'); ax.set_xlim(*FULL['xlim']); ax.set_ylim(*FULL['ylim'])
ax.set_title('全体配置（17mmピッチ）：新外形＝実線、現行 Rev.8／Rev.5＝破線', fontsize=12)
fig.text(0.5, 0.015, 'Main：60°台形タブ（左右同一仕様）　Wing：ノッチをタブに平行に再整形、継ぎ目 0.55mm 一様（現行 0.521／0.522）',
         ha='center', fontsize=10.5)
fig.tight_layout(rect=(0, 0.04, 1, 0.97))
fig.savefig('fig-s2a-layout.png', dpi=130)
plt.close(fig)
print('saved fig-s2a-layout.png')


# ---------------- seam zooms ----------------
def zoom_fig(side, ref, win, fname, wall_note_xy, gap_xy):
    cur_w = wing_cur(side)
    new_w = wing_new(side)
    fig, axes = plt.subplots(1, 3, figsize=(14.5, 5.6))
    for ax, title, mpoly, wpoly, dashed in (
            (axes[0], '現行：Rev.8 ＋ Rev.5', rev8, cur_w, False),
            (axes[1], '新案：60°タブ ＋ 再整形ノッチ', main_new, new_w, False),
            (axes[2], '重ね合わせ（破線＝現行）', main_new, new_w, True)):
        wcol = '#2b6cb0' if side == 'left' else '#c05621'
        ax.add_patch(MplPoly(wpoly, closed=True, facecolor=wcol,
                             alpha=0.10, edgecolor='none', zorder=2))
        ax.plot([c[0] for c in wpoly] + [wpoly[0][0]], [c[1] for c in wpoly] + [wpoly[0][1]],
                color=wcol, lw=1.4, zorder=2.5)
        if dashed:
            ax.add_patch(MplPoly(cur_w, closed=True, facecolor='none', edgecolor='#888888',
                                 lw=1.0, linestyle=(0, (4, 3)), zorder=3))
            ax.add_patch(MplPoly(rev8, closed=True, facecolor='none', edgecolor='#888888',
                                 lw=1.0, linestyle=(0, (4, 3)), zorder=3))
        ax.add_patch(MplPoly(mpoly, closed=True, facecolor='#e53e3e', alpha=0.15,
                             edgecolor='none', zorder=4))
        ax.plot([c[0] for c in mpoly] + [mpoly[0][0]], [c[1] for c in mpoly] + [mpoly[0][1]],
                color='#c53030', lw=1.8, zorder=4.5)
        for c in pads:
            ax.add_patch(MplPoly(c, closed=True, facecolor='#4a5568', edgecolor='none', zorder=5))
        ax.set_aspect('equal')
        ax.set_xlim(win[0], win[1]); ax.set_ylim(win[3], win[2])
        ax.set_title(title, fontsize=11.5)
        ax.tick_params(labelsize=8)
    axes[1].annotate('タブ壁 60°\n（基板斜辺に対して）', xy=wall_note_xy, fontsize=10,
                     ha='center', color='#9b2c2c', fontweight='bold')
    axes[1].annotate('ノッチ面はタブに平行\n継ぎ目 0.55mm 一様', xy=gap_xy, fontsize=10,
                     ha='center', color='#2c5282', fontweight='bold')
    axes[0].annotate('現行：四角タブ＋\nタブに合わせたノッチ\n（継ぎ目 0.521／0.522）', xy=gap_xy, fontsize=10, ha='center')
    fig.suptitle(f'{ref} 側の継ぎ目拡大（同縮尺）', fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(fname, dpi=130)
    plt.close(fig)
    print('saved', fname)


zoom_fig('left', 'J2（左）', (-38, -13, 27, 56), 'fig-s2a-zoom-j2.png', (-27.5, 52.5), (-26, 30.5))
zoom_fig('right', 'J3（右）', (13, 38, 27, 56), 'fig-s2a-zoom-j3.png', (27.5, 52.5), (26, 30.5))
