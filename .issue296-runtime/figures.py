#!/usr/bin/env python3
"""Stage B 2D figures. Frame: asm (X centred, +east; Y +south).
All dimensioned elements from board files / study artifacts (sources in
case-2d-stageb.md). Wing outer bodies are schematic (bbox of record);
inner-edge profiles are the measured ones from the wing-shape study."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
import matplotlib.font_manager as fm

for f in fm.findSystemFonts():
    if 'NotoSansCJK' in f: plt.rcParams['font.family'] = fm.FontProperties(fname=f).get_name()
plt.rcParams['axes.unicode_minus'] = False

OUT = "/home/hatch/workspace/goals/he-piantor-42-keyboard-pmo/files/"
EDG = dict(ec='#333', lw=0.8)

def wing_inner(ax, side, y0=-64, y1=82):
    s = side  # +1 right, -1 left
    # board inner edge (baseline profile + delta 9.5): straight X=13.0->22.5
    ax.plot([s*22.5, s*22.5], [-47, -19], color='#1a5276', lw=1.6)
    ax.plot([s*22.5, s*27.92], [-19, -15], color='#1a5276', lw=1.6)
    ax.plot([s*27.92, s*27.92], [-15, -11], color='#1a5276', lw=1.6)
    ax.plot([s*27.92, s*10.5], [-11, 0], color='#1a5276', lw=1.6)
    # plate inner edge: straight 13.2->22.7, tip diagonal to (11.45,-0.76), notch cut X=22.47
    ax.plot([s*22.7, s*22.7], [-53.75, -17.64], color='#b03a2e', lw=1.4)
    ax.plot([s*22.7, s*22.47], [-17.64, -17.28], color='#b03a2e', lw=1.4)
    ax.plot([s*22.47, s*22.47], [-17.28, -0.76], color='#b03a2e', lw=1.4, ls='--')
    ax.add_patch(Polygon([[s*11.45,-0.76],[s*22.47,-0.76],[s*22.47,-17.28]],
                 closed=True, fc='#f5b7b1', ec='#b03a2e', lw=0.7, hatch='//'))

fig, axes = plt.subplots(1, 3, figsize=(19, 8.2), gridspec_kw={'width_ratios':[2.2,1,1]})
ax = axes[0]
ax.add_patch(Rectangle((-155,-64.37), 310, 146.07, fc='#f8f8f5', **EDG))
ax.add_patch(Rectangle((-155,-64.37), 310, 2.0, fc='#d5d8dc', ec='none'))  # north wall
ax.add_patch(Rectangle((-155,79.70), 310, 2.0, fc='#d5d8dc', ec='none'))   # south wall
# Main slab (record: X +-37.89, Y 2.27..67.90)
ax.add_patch(Rectangle((-37.89,2.27), 75.78, 65.63, fc='#aed6f1', ec='#1a5276', lw=1.0))
ax.text(0, 60, 'Main 基板\n(無線, D-063)', ha='center', fontsize=8, color='#1a5276')
# Wing bodies: real Edge.Cuts outline of 17R (PR #300 @3fcad246f) transformed
# to the asm frame (fit verified: bbox X 1.0..142.244, Y -61.6..77.38) + delta 9.5
import json as _json
_segs = _json.load(open('.issue296-runtime/wing17r-outline-asm.json'))
for s in (1,-1):
    for sg in _segs:
        pts = [[s*(p[0]+9.5), p[1]] for p in sg[1:]]
        if sg[0]=='line':
            ax.plot([pts[0][0],pts[1][0]],[pts[0][1],pts[1][1]], color='#1a5276', lw=0.55, alpha=0.75)
        else:
            ax.plot([p[0] for p in pts],[p[1] for p in pts], color='#1a5276', lw=0.55, alpha=0.75)
    wing_inner(ax, s)
    ax.text(s*100, 55, 'Wing 基板 17%s\n(実外形・不変)' % ('R' if s>0 else 'L'), ha='center', fontsize=8, color='#1a5276')
# centre bay cavity + power board + block
ax.add_patch(Rectangle((-28.25,-62.37), 56.5, 60.0, fc='#fdebd0', ec='#935116', lw=1.0))
ax.add_patch(Rectangle((-26.25,-62.37), 52.5, 58.0, fc='#f39c6b', ec='#935116', lw=1.0))
ax.add_patch(Rectangle((-24.25,-62.37), 48.5, 56.0, fc='none', ec='#7d3c98', lw=1.2, ls='--'))
for cx in (-15,0,15):
    ax.add_patch(Circle((cx,-34.37), 7.25, fc='#e8daef', ec='#7d3c98', lw=1.0))
ax.text(0, -34.37, 'AA×3', ha='center', va='center', fontsize=8, color='#7d3c98')
ax.text(0, -58.5, '電源基板 52.5×58.0', ha='center', fontsize=7.5, color='#935116')
# Fly right
ax.add_patch(Rectangle((38-11.79,-50.14-4.15), 23.57, 8.30, fc='#82e0aa', ec='#145a32', lw=1.0))
ax.text(38, -50.14, 'Fly', ha='center', va='center', fontsize=8, color='#145a32')
ax.plot([38,38], [-64.37,-54.3], color='#145a32', lw=1.2, ls=':')  # USB opening to gable
ax.text(41, -60, 'USB開口\n(北ゲーブル壁)', fontsize=7, color='#145a32')
# trackpad island
ax.add_patch(Circle((0,48), 22, fc='#f9e79f', ec='#7d6608', lw=1.0, alpha=0.8))
ax.text(0, 48, 'トラックパッド島\nØ44', ha='center', va='center', fontsize=7.5, color='#7d6608')
# routes
ax.plot([0,35.75,38],[19.2,-6,-49.0], color='#145a32', lw=1.6, ls='-')   # EZmate
ax.text(30, 8, 'EZmate ≈87\n(+余裕≈100)', fontsize=7, color='#145a32')
ax.plot([17,-0+30,24,24],[-4,10,60,67.9], color='#935116', lw=1.6)      # JBATT route
ax.text(27.5, 30, 'JBATT ≈100級', fontsize=7, color='#935116', rotation=90)
ax.plot([24.255,36.5],[45.22,-38.9], color='#1a5276', lw=1.4, ls='--')  # FFC right span
ax.plot([-24.255,-36.5],[45.22,-38.9], color='#1a5276', lw=1.4, ls='--')
ax.text(33, 2, 'FFC 中心間 85.0', fontsize=7, color='#1a5276', rotation=90)
# points: SW1, DLED, JBATT, switch
ax.plot(-15.5, 67.9, marker='s', color='#b03a2e', ms=6); ax.text(-33, 71, 'SW1 (−15.5, 67.9)\nプランジャ穴', fontsize=7, color='#b03a2e')
ax.plot(-4.0, 16.4, marker='o', color='#b7950b', ms=6); ax.text(-52, 12, 'DLED (−4.0, 16.4)\nライトパイプ Ø2', fontsize=7, color='#7d6608')
ax.plot(24.0, 67.9, marker='s', color='#935116', ms=6); ax.text(26, 71, 'JBATT', fontsize=7, color='#935116')
ax.plot(28.25, -34.37, marker='>', color='#333', ms=8); ax.text(31, -30, 'スライドスイッチ\n(ベイ東壁)', fontsize=7)
ax.annotate('', xy=(155,-68), xytext=(-155,-68), arrowprops=dict(arrowstyle='<->', lw=0.8))
ax.text(0, -71.5, '外形 310', ha='center', fontsize=9)
ax.annotate('', xy=(158.5,81.70), xytext=(158.5,-64.37), arrowprops=dict(arrowstyle='<->', lw=0.8))
ax.text(160, 8, '146.1', fontsize=9, rotation=90, va='center')
ax.set_xlim(-168, 172); ax.set_ylim(84, -76); ax.set_aspect('equal'); ax.axis('off')
ax.set_title('上面図 — D-062 + δ=9.5（プレート先端ノッチ）', fontsize=11)

ax = axes[1]  # bay zoom
ax.add_patch(Rectangle((-28.25,-62.37), 56.5, 60.0, fc='#fdebd0', ec='#935116'))
ax.add_patch(Rectangle((-26.25,-62.37), 52.5, 58.0, fc='#f39c6b', ec='#935116'))
ax.add_patch(Rectangle((-24.25,-62.37), 48.5, 56.0, fc='none', ec='#7d3c98', lw=1.4, ls='--'))
for cx in (-15,0,15):
    ax.add_patch(Circle((cx,-34.37), 7.25, fc='#e8daef', ec='#7d3c98', lw=1.4))
    ax.plot([cx,cx],[-60.37,-8.37], color='#7d3c98', lw=0.5, ls=':')
ax.plot([-24.25,-24.25],[-60.37,-8.37], color='#333', lw=0.7)
ax.text(-23, -12, '接点面 ±26.00\n(セル中心基準)', fontsize=7)
wing_inner(ax, 1); wing_inner(ax, -1)
ax.text(0, -66.5, 'ベイ内腔 56.5×60.0 / 床 Z −0.65（均し）', ha='center', fontsize=8)
ax.text(0, 2.5, 'ブロック包絡 48.5×56.0（北寄せ）', ha='center', fontsize=8, color='#7d3c98')
ax.set_xlim(-45, 45); ax.set_ylim(6, -70); ax.set_aspect('equal'); ax.axis('off')
ax.set_title('ベイ拡大', fontsize=11)

ax = axes[2]  # south zoom
ax.add_patch(Rectangle((-37.89,2.27), 75.78, 65.63, fc='#aed6f1', ec='#1a5276'))
ax.add_patch(Rectangle((-60,79.70), 120, 2.0, fc='#d5d8dc', ec='none'))
ax.add_patch(Rectangle((-60,67.90), 120, 11.80, fc='#fdebd0', ec='#b7950b', lw=0.8))
ax.text(0, 74, 'アンテナ帯 PETG 11.8（金属物なし）', ha='center', fontsize=7.5, color='#7d6608')
ax.plot(-15.5, 67.9, marker='s', color='#b03a2e', ms=7); ax.text(-52, 62, 'SW1', fontsize=8, color='#b03a2e')
ax.plot(24.0, 67.9, marker='s', color='#935116', ms=7); ax.text(27, 62, 'JBATT', fontsize=8, color='#935116')
ax.plot(-4.0, 16.4, marker='o', color='#b7950b', ms=7); ax.text(-40, 13, 'DLED', fontsize=8, color='#7d6608')
ax.add_patch(Circle((0,48), 22, fc='#f9e79f', ec='#7d6608', alpha=0.8))
ax.text(0, 48, '島 Ø44', ha='center', va='center', fontsize=8, color='#7d6608')
ax.plot([24.255,36.5],[45.22,-10], color='#1a5276', lw=1.4, ls='--')
ax.text(38, 25, 'FFCチャネル 11.5', fontsize=8, color='#1a5276', rotation=90)
ax.set_xlim(-60, 60); ax.set_ylim(84, -14); ax.set_aspect('equal'); ax.axis('off')
ax.set_title('南側拡大（Main/アンテナ帯）', fontsize=11)
fig.tight_layout(); fig.savefig(OUT+'case296b-2d-topview.png', dpi=150); plt.close(fig)

# ---- sections ----
fig, axes = plt.subplots(1, 3, figsize=(19, 6.4), gridspec_kw={'width_ratios':[1.25,1.25,1]})
ax = axes[0]  # N-S section at X=+7.5 (through east cell)
ax.add_patch(Rectangle((-62.37,-2.65), 56.0, 2.0, fc='#d5d8dc', ec='#333'))       # case floor slab (top -0.65)
ax.add_patch(Rectangle((-62.37,-0.65), 56.0, 0.8, fc='#f39c6b', ec='#935116'))      # power board
ax.add_patch(Circle((-34.37,7.4), 7.25, fc='#e8daef', ec='#7d3c98', lw=1.2))        # cell (centre Z = -0.65+0.8+7.25=7.4 rel? use case Z axis)
# NOTE: draw with Z vertical: redo coordinates properly below
plt.close(fig)
fig, axes = plt.subplots(1, 3, figsize=(19, 6.4), gridspec_kw={'width_ratios':[1.25,1.25,1]})
ax = axes[0]
# axes: x = Y (north -62 left .. south +82 right), y = case Z
ax.add_patch(Rectangle((-64.37,-2.65), 146.07, 2.0, fc='#d5d8dc', ec='#333', lw=0.7))  # case bottom slab, top -0.65 in bay zone only approx
ax.add_patch(Rectangle((-62.37,-0.65), 56.0, 0.8, fc='#f39c6b', ec='#935116'))
# cell as stadium: body Y -59.62..-9.12 (50.5 long), Z 0.15..14.65
ax.add_patch(Rectangle((-59.62,0.15), 50.5, 14.5, fc='#e8daef', ec='#7d3c98', lw=1.3))
ax.add_patch(Rectangle((-62.37,14.65), 56.0, 2.0, fc='#aeb6bf', ec='#333'))  # cover top 16.65
ax.add_patch(Rectangle((-50,-0.65), 30, 5.35, fc='none', ec='#b03a2e', lw=1.0, ls='--'))  # removed moulding ghost (top 4.70)
ax.text(-35, 3.2, '除去する旧成形\n(上面 4.70)', fontsize=7, color='#b03a2e', ha='center')
ax.add_patch(Rectangle((2.27,9.40), 65.63, 1.5, fc='#aed6f1', ec='#1a5276'))  # plate south part
ax.axhline(22.0, color='#b03a2e', lw=1.2); ax.text(60, 22.6, 'キートップ基準 22.00', color='#b03a2e', fontsize=8)
ax.axhline(16.65, color='#333', lw=0.7, ls=':'); ax.text(-64, 17.3, 'カバー上面 16.65（余裕 5.35）', fontsize=8)
ax.axhline(14.65, color='#7d3c98', lw=0.7, ls=':'); ax.text(-64, 12.6, 'セル上面 14.65', fontsize=8, color='#7d3c98')
ax.axhline(-0.65, color='#935116', lw=0.7, ls=':'); ax.text(-64, -1.8, '均した床 −0.65', fontsize=8, color='#935116')
ax.text(-34.37, 7.4, 'AA (軸=南北)', ha='center', va='center', fontsize=9, color='#7d3c98')
ax.set_xlim(-70, 88); ax.set_ylim(-4, 26); ax.set_xlabel('Y（左=北）'); ax.set_ylabel('case Z')
ax.set_title('南北断面 X=+7.5（東セル通過）', fontsize=11); ax.grid(alpha=0.25)

ax = axes[1]  # E-W section at Y=-34.37
ax.add_patch(Rectangle((-28.25,-2.65), 56.5, 2.0, fc='#d5d8dc', ec='#333', lw=0.7))
ax.add_patch(Rectangle((-26.25,-0.65), 52.5, 0.8, fc='#f39c6b', ec='#935116'))
for cx in (-15,0,15):
    ax.add_patch(Circle((cx,7.4), 7.25, fc='#e8daef', ec='#7d3c98', lw=1.3))
ax.add_patch(Rectangle((-28.25,14.65), 56.5, 2.0, fc='#aeb6bf', ec='#333'))
ax.add_patch(Rectangle((-28.25,-0.65), 2.0, 17.3, fc='#aeb6bf', ec='#333'))
ax.add_patch(Rectangle((26.25,-0.65), 2.0, 17.3, fc='#aeb6bf', ec='#333'))
ax.axhline(22.0, color='#b03a2e', lw=1.2); ax.text(10, 22.6, '基準 22.00', color='#b03a2e', fontsize=8)
ax.text(0, 18.3, 'カバー（上面 16.65）', ha='center', fontsize=8)
ax.text(0, -4.3, '壁厚 2.0 / 接点クリップ部 1.52–1.78 を壁内面に形成', ha='center', fontsize=7.5)
ax.set_xlim(-34, 34); ax.set_ylim(-6, 26); ax.set_xlabel('X'); ax.set_ylabel('case Z')
ax.set_title('東西断面 Y=−34.37（ベイ中央）', fontsize=11); ax.grid(alpha=0.25)

ax = axes[2]  # south band / DLED section at X=-4
ax.add_patch(Rectangle((2.27,-2.65), 79.43, 2.0, fc='#d5d8dc', ec='#333', lw=0.7))
ax.add_patch(Rectangle((2.27,4.70), 65.63, 1.2, fc='#aed6f1', ec='#1a5276'))  # Main board (underside 4.70)
ax.plot(16.4, 5.9, marker='o', color='#b7950b', ms=7)
ax.add_patch(Rectangle((15.4,5.9), 2.0, 8.0, fc='#f9e79f', ec='#7d6608'))  # light pipe
ax.text(19, 10, 'ライトパイプ Ø2\nDLED (−4.0, 16.4) から\nスパイン表面へ', fontsize=7.5, color='#7d6608')
ax.add_patch(Rectangle((67.90,-0.65), 11.80, 1.0, fc='#fdebd0', ec='#b7950b'))
ax.text(73.8, 2.2, 'アンテナ帯\n11.8', ha='center', fontsize=8, color='#7d6608')
ax.axhline(22.0, color='#b03a2e', lw=1.0)
ax.set_xlim(-2, 86); ax.set_ylim(-4, 26); ax.set_xlabel('Y（左=北）'); ax.set_ylabel('case Z')
ax.set_title('南帯・DLED 断面 X=−4', fontsize=11); ax.grid(alpha=0.25)
fig.tight_layout(); fig.savefig(OUT+'case296b-2d-sections.png', dpi=150); plt.close(fig)
print('figures written')
