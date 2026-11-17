"""Issue #270 stage 2c figures: clean 2D outline drawings (no shading).
Full Main+Wing views (current Rev.9/Rev.6 vs candidate) at identical
scale, and per-site zooms with connector outline + angle lines.
Run with system python3 from a clean cwd; paths absolute.
"""
import json, math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Polygon as MplPoly

RT = Path('/home/hatch/workspace/projects/he-piantor-mainoutline/.issue270-runtime')
FILES = Path('/home/hatch/workspace/goals/he-piantor-42-keyboard-pmo/files')
font_manager.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
plt.rcParams['font.family'] = 'Noto Sans CJK JP'

polys = json.loads((RT / 'stage2c-polys.json').read_text())
res = json.loads((RT / 'stage2c.json').read_text())
meas = json.loads((RT / 'stage2c-measure.json').read_text())
probe = json.loads((RT / 'stage2c-probe.json').read_text())
g = json.loads((RT / 'geometry.json').read_text())
M = res['measure']

C_MAIN = '#111111'
C_WING = '#777777'
C_CONN = '#0057b8'
C_AXIS = '#c0272d'
C_EDGE = '#888888'


def draw_ring(ax, ring, color, lw=1.2, ls='-', z=3):
    xs = [p[0] for p in ring] + [ring[0][0]]
    ys = [p[1] for p in ring] + [ring[0][1]]
    ax.plot(xs, ys, color=color, lw=lw, ls=ls, zorder=z)


def draw_connector(ax, ref, z=4):
    cy = probe[ref]['courtyard'][0][1]
    draw_ring(ax, cy, C_CONN, lw=1.1, z=z)
    for pd in g['main_zif_pads'][ref]:
        bb = pd['bbox']
        cx = sum(p[0] for p in bb) / len(bb)
        cy_ = sum(p[1] for p in bb) / len(bb)
        bb = sorted(bb, key=lambda p: math.atan2(p[1] - cy_, p[0] - cx))
        ax.add_patch(MplPoly(bb, closed=True, fill=False, ec=C_CONN, lw=0.5, zorder=z))


def setup(ax, xlim, ylim, title):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect('equal')
    ax.set_title(title, fontsize=13)
    ax.tick_params(labelsize=8)
    ax.grid(True, color='#dddddd', lw=0.4, zorder=0)


# ---------- full views ----------
allx, ally = [], []
for ring in [polys['main_rev9'], polys['main_cand']]:
    allx += [p[0] for p in ring]
    ally += [p[1] for p in ring]
for v in ('17mm-left', '17mm-right'):
    for k in ('rev6', 'cand'):
        allx += [p[0] for p in polys['wings'][v][k]]
        ally += [p[1] for p in polys['wings'][v][k]]
pad = 4
XL = (min(allx) - pad, max(allx) + pad)
YL = (min(ally) - pad, max(ally) + pad)
W = 11.0
H = W * (YL[1] - YL[0]) / (XL[1] - XL[0])

for tag, main_key, wing_key, title in (
        ('current', 'main_rev9', 'rev6', '現行：Main Rev.9 ＋ Wing Rev.6（17mm配置）'),
        ('candidate', 'main_cand', 'cand', '候補：コネクタ平行タブ ＋ 追従ノッチ（17mm配置）')):
    fig, ax = plt.subplots(figsize=(W, H))
    draw_ring(ax, polys['wings']['17mm-left'][wing_key], C_WING, lw=1.0)
    draw_ring(ax, polys['wings']['17mm-right'][wing_key], C_WING, lw=1.0)
    draw_ring(ax, polys[main_key], C_MAIN, lw=1.4)
    draw_connector(ax, 'J2')
    draw_connector(ax, 'J3')
    setup(ax, XL, YL, title)
    fig.tight_layout()
    out = RT / f'fig-2c-full-{tag}.png'
    fig.savefig(out, dpi=200)
    fig.savefig(FILES / out.name, dpi=200)
    plt.close(fig)
    print('saved', out.name)

# ---------- overlay ----------
fig, ax = plt.subplots(figsize=(W, H))
draw_ring(ax, polys['main_rev9'], '#999999', lw=1.2)
draw_ring(ax, polys['main_cand'], C_AXIS, lw=1.2)
setup(ax, XL, YL, '重ね図：灰＝Rev.9、赤＝候補（Main外形のみ）')
fig.tight_layout()
fig.savefig(RT / 'fig-2c-overlay.png', dpi=200)
fig.savefig(FILES / 'fig-2c-overlay.png', dpi=200)
plt.close(fig)
print('saved fig-2c-overlay.png')

# ---------- zooms ----------
for ref, variant, name in (('J2', '17mm-left', 'j2'), ('J3', '17mm-right', 'j3')):
    d = M[ref]
    cen = d['cen']
    half = 17.0
    xl = (cen[0] - half, cen[0] + half)
    yl = (cen[1] - half, cen[1] + half)
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 6.2))
    for ax, main_key, wing_key, ttl in (
            (axes[0], 'main_rev9', 'rev6', '現行 Rev.9'),
            (axes[1], 'main_cand', 'cand', '候補')):
        draw_ring(ax, polys['wings'][variant][wing_key], C_WING, lw=1.0)
        draw_ring(ax, polys[main_key], C_MAIN, lw=1.5)
        draw_connector(ax, ref)
        a, u = d['a'], d['u']
        for vec, col, lab in ((u, C_EDGE, f"基板の斜め縁 {d['edge_line_ang']:.0f}°"),
                              (a, C_AXIS, f"コネクタ軸 {d['axis_line_ang']:.0f}°")):
            ax.plot([cen[0] - vec[0] * 15, cen[0] + vec[0] * 15],
                    [cen[1] - vec[1] * 15, cen[1] + vec[1] * 15],
                    color=col, lw=0.9, ls='--', zorder=2)
            ax.text(cen[0] + vec[0] * 15.5, cen[1] + vec[1] * 15.5, lab,
                    fontsize=8.5, color=col, ha='center', va='center')
        setup(ax, xl, yl, f'{ref} {ttl}（ズレ {d["skew_deg"]:.1f}°）')
    fig.tight_layout()
    out = RT / f'fig-2c-zoom-{name}.png'
    fig.savefig(out, dpi=200)
    fig.savefig(FILES / out.name, dpi=200)
    plt.close(fig)
    print('saved', out.name)
print('done')
