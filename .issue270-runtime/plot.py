"""Issue #270 stage 1 figures: fig-current.png, fig-cand-A/B/C.png.
Same framing for all: left = full flat layout (case silhouette,
Wing Rev.5 L/R + keys, Main), right = zoom on Main's north region
(candidate bold, current dashed, ZIF pads, Wing notch zone)."""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Polygon as MplPoly, Rectangle

font_manager.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
plt.rcParams['font.family'] = 'Noto Sans CJK JP'

g = json.load(open('geometry.json'))
cand = json.load(open('candidates.json'))
res = cand['results']

sil = json.load(open('case_geometry.json'))['silhouette_parts']
rev8 = g['main_rev8_outline']
wings = {s: g['wings'][s] for s in ('left', 'right')}
pads = []
for ref, lst in g['main_zif_pads'].items():
    for pd in lst:
        pads.append(pd['corners'])

FULL = dict(xlim=(-152, 152), ylim=(88, -72))
ZOOM = dict(xlim=(-46, 46), ylim=(58, -4))


def draw_layout(ax, main_poly, main_kw, extra=None):
    for part in sil:
        ax.add_patch(MplPoly(part, closed=True, facecolor='#e8e8e8', edgecolor='#aaaaaa', lw=0.8, zorder=0))
    for side, col in (('left', '#2b6cb0'), ('right', '#c05621')):
        o = wings[side]['outline']
        ax.add_patch(MplPoly(o, closed=True, facecolor=col, alpha=0.10, edgecolor=col, lw=1.1, zorder=2))
        kx = [k[0] for k in wings[side]['keys']]
        ky = [k[1] for k in wings[side]['keys']]
        ax.plot(kx, ky, '.', color=col, ms=4, zorder=3)
    ax.add_patch(MplPoly(main_poly, closed=True, facecolor='#e53e3e', alpha=0.13,
                         edgecolor=main_kw.get('color', '#c53030'), lw=main_kw.get('lw', 1.4), zorder=4))
    for c in pads:
        ax.add_patch(MplPoly(c, closed=True, facecolor='#4a5568', edgecolor='none', zorder=5))
    if extra:
        extra(ax)
    ax.set_aspect('equal')
    ax.set_xlim(*FULL['xlim']); ax.set_ylim(*FULL['ylim'])
    ax.tick_params(labelsize=7)


def draw_zoom(ax, main_poly, main_kw, extra=None):
    for side, col in (('left', '#2b6cb0'), ('right', '#c05621')):
        o = wings[side]['outline']
        ax.add_patch(MplPoly(o, closed=True, facecolor=col, alpha=0.10, edgecolor=col, lw=1.1, zorder=2))
    ax.add_patch(MplPoly(rev8, closed=True, facecolor='none', edgecolor='#888888',
                         lw=0.9, linestyle=(0, (4, 3)), zorder=3))
    ax.add_patch(MplPoly(main_poly, closed=True, facecolor='#e53e3e', alpha=0.15,
                         edgecolor=main_kw.get('color', '#c53030'), lw=1.8, zorder=4))
    for c in pads:
        ax.add_patch(MplPoly(c, closed=True, facecolor='#4a5568', edgecolor='none', zorder=5))
    ax.annotate('J2 (ZIF)', xy=(-24.5, 36.2), fontsize=8, ha='center', zorder=6)
    ax.annotate('J3 (ZIF)', xy=(24.9, 36.2), fontsize=8, ha='center', zorder=6)
    if extra:
        extra(ax)
    ax.set_aspect('equal')
    ax.set_xlim(*ZOOM['xlim']); ax.set_ylim(*ZOOM['ylim'])
    ax.tick_params(labelsize=7)


def make(fname, title, key, note, extra_full=None, extra_zoom=None):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13.5, 6.8), gridspec_kw={'width_ratios': [1.55, 1]})
    poly = cand['polys'][key] if key != 'current' else rev8
    draw_layout(a1, poly, {}, extra_full)
    draw_zoom(a2, poly, {}, extra_zoom)
    a1.set_title('全体配置（17mmピッチ、ケース外形つき）', fontsize=10)
    a2.set_title('Main北側の拡大（破線＝現行Rev.8）', fontsize=10)
    fig.suptitle(title, fontsize=13)
    fig.text(0.5, 0.015, note, ha='center', fontsize=9.5)
    fig.tight_layout(rect=(0, 0.045, 1, 0.95))
    fig.savefig(fname, dpi=130)
    plt.close(fig)
    print('saved', fname)


def mmss(v):
    return f"{v:.3f}"


r = res['current']
make('fig-current.png', '現行：Main Rev.8 ＋ Wing Rev.5（低デッキ構成）', 'current',
     f"タブは最小拡張の四角形（J2 4.738mm／J3 4.721mm、左右非対称）　"
     f"継ぎ目 {r['seam_L']:.3f}／{r['seam_R']:.3f}mm　パッド余裕 {r['pad_clearance']:.3f}mm")

r = res['A']
make('fig-cand-A.png', '候補A：角を丸めたタブ（フィレット）', 'A',
     f"前面の角 R2.0＋付け根フィレット R2.0　継ぎ目 {r['seam_L']:.3f}／{r['seam_R']:.3f}mm（現行以上）　"
     f"パッド余裕 {r['pad_clearance']:.3f}mm　トレイ追加リリーフ +0.37／+0.37mm³　銅箔カット なし")

r = res['C']
make('fig-cand-C.png', '候補C：左右同一仕様の台形タブ', 'C',
     f"深さ4.738mm・前幅16.689mm・壁1.0mmランで左右同一　継ぎ目 {r['seam_L']:.3f}／{r['seam_R']:.3f}mm　"
     f"パッド余裕 {r['pad_clearance']:.3f}mm　トレイ追加 +0.66／+0.78mm³　銅箔カット なし")


def hatch_overlap(ax):
    for q in cand['b_overlap']:
        ax.add_patch(MplPoly(q, closed=True, facecolor='red', alpha=0.45,
                             edgecolor='darkred', hatch='///', zorder=7))


r = res['B']
make('fig-cand-B.png', '候補B：連続エッジ（不可：Wingと干渉）', 'B',
     '前面を頂点まで延長し R12 で接続 → Wing外形と各約96mm²重なる（継ぎ目 0mm）。'
     'タブ間区間の Wing は Rev.7 エッジから 1.516mm しか離れておらず、連続化には Wing 全面ノッチ（再設計）が必要',
     extra_full=hatch_overlap, extra_zoom=hatch_overlap)
