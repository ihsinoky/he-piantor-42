"""Render v2 figures from extracted real geometry. System python3 + matplotlib.
All shapes come from geom_v2.json / main-outline-asm.json /
wing17r-outline-asm.json (see case-2d-stageb.md addendum for sources).
Asm frame: X east, Y south. Case Z = g17 Z - 2.65.
Main transform (CORRECTED, see addendum): X = bx-100, Y = by-70.0.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Polygon, Circle, Rectangle, PathPatch
from matplotlib.path import Path
import json

font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "/home/hatch/workspace/goals/he-piantor-42-keyboard-pmo/files/"

G = json.load(open(".issue296-runtime/geom_v2.json"))
MAIN = json.load(open(".issue296-runtime/main-outline-asm.json"))
WING = json.load(open(".issue296-runtime/wing17r-outline-asm.json"))

def clip_half(poly, keep_ge, c):
    """Sutherland-Hodgman clip of ordered polygon against x>=c (keep_ge)
    or x<=c."""
    def inside(p):
        return p[0] >= c if keep_ge else p[0] <= c
    def cross(a, b):
        t = (c - a[0]) / (b[0] - a[0])
        return [c, a[1] + t * (b[1] - a[1])]
    out = []
    n = len(poly)
    for i in range(n):
        cur, prv = poly[i], poly[i - 1]
        if inside(cur):
            if not inside(prv):
                out.append(cross(prv, cur))
            out.append(cur)
        elif inside(prv):
            out.append(cross(prv, cur))
    return out

def stadium(cx, cy, R=7.25, L=36.0):  # straight section; total length = L + 2R = 50.5 (AA cell)
    import math
    pts = [[cx + R, cy - L / 2], [cx + R, cy + L / 2]]
    for k in range(1, 13):  # south cap (bulges +Y)
        a = math.pi * k / 12
        pts.append([cx + R * math.cos(a), cy + L / 2 + R * math.sin(a)])
    pts.append([cx - R, cy - L / 2])
    for k in range(1, 12):  # north cap (bulges -Y)
        a = math.pi + math.pi * k / 12
        pts.append([cx + R * math.cos(a), cy - L / 2 + R * math.sin(a)])
    return pts

# ================= TOP VIEW =================
fig, ax = plt.subplots(figsize=(13.5, 7.6))
ax.set_aspect("equal"); ax.axis("off")
ax.set_xlim(-168, 168); ax.set_ylim(92, -76)
ax.set_title("無線ケース Stage B 2D（実形状・上面図）— 外形 310 × 146.1 / δ=9.5（プレート先端ノッチ）",
             fontsize=12.5, weight="bold", pad=10)

# case: projected edges of the real solids (trays shifted +-9.5, shell, strips)
for name, lines in G["case_edges"].items():
    for pts in lines:
        ax.plot([p[0] for p in pts], [p[1] for p in pts],
                color="#6b7a89", lw=0.5, alpha=0.85, zorder=1)

# Wing boards: real Edge.Cuts (17R), right shifted +9.5, left mirrored
for s in (1, -1):
    for sg in WING:
        pts = [[s * (p[0] + 9.5), p[1]] for p in sg[1:]]
        ax.plot([p[0] for p in pts], [p[1] for p in pts],
                color="#1a5276", lw=0.7, alpha=0.9, zorder=3)
ax.text(105, 62, "Wing基板 17R（実外形）", fontsize=8.5, color="#1a5276", ha="center")
ax.text(-105, 62, "Wing基板 17L（実外形）", fontsize=8.5, color="#1a5276", ha="center")

# Main board: real Edge.Cuts polygon (D-063 file, corrected transform)
segs = [([a[0], a[1]], [b[0], b[1]]) for a, b in MAIN]
mp = [segs[0][0], segs[0][1]]
segs = segs[1:]
while segs:
    for i, (a, b) in enumerate(segs):
        if a == mp[-1]:
            mp.append(b); segs.pop(i); break
        if b == mp[-1]:
            mp.append(a); segs.pop(i); break
    else:
        break
ax.add_patch(Polygon(mp, closed=True, fc="#aed6f1", ec="#1a5276", lw=1.1, alpha=0.75, zorder=2))
ax.text(0, 63, "Main基板（実外形）", fontsize=8.5, color="#1a5276", ha="center")

# plates: real top-face outlines, tip notch clipped at |X|=22.47
for name, keep_ge, c in [("plate-right", True, 22.47), ("plate-left", False, -22.47)]:
    outer = G["plates"][name]["outer"]
    clipped = clip_half(outer, keep_ge, c)
    ax.add_patch(Polygon(clipped, closed=True, fc="#d6eaf8", ec="#2e5f8a",
                         lw=1.0, alpha=0.55, zorder=2))
    removed = clip_half(outer, not keep_ge, c)
    if len(removed) > 2:
        ax.add_patch(Polygon(removed, closed=True, fc="none", ec="#c0392b",
                             lw=1.1, ls=(0, (4, 2)), zorder=4))
    for hx, hy, hr in G["plates"][name]["holes"]:
        ax.add_patch(Circle((hx, hy), hr, fc="white", ec="#2e5f8a", lw=0.5, zorder=3))
ax.annotate("プレート先端ノッチ\n（切断線 |X|=22.47・赤破線=除去部）",
            xy=(24.5, -18), xytext=(58, -34), fontsize=8.5, color="#c0392b",
            arrowprops=dict(arrowstyle="-", color="#c0392b", lw=0.9))

# centre bay: cavity walls, power board (Stage-2 outline), cells (true cylinders)
ax.add_patch(Rectangle((-30.25, -64.37), 60.5, 64.0, fc="#e8e3d8", ec="#5d4a2f", lw=1.2, zorder=3))
ax.add_patch(Rectangle((-28.25, -62.37), 56.5, 60.0, fc="#fdebd0", ec="#935116", lw=1.1, zorder=3))
ax.annotate("北辺中央はベイに合わせ −64.37 へ再形成", xy=(-30.25, -64.37), xytext=(-160, -72),
            fontsize=8, color="#5d4a2f",
            arrowprops=dict(arrowstyle="-", color="#5d4a2f", lw=0.8))
ax.add_patch(Rectangle((-26.25, -62.37), 52.5, 58.0, fc="#f5b041", ec="#935116", lw=0.9, alpha=0.5, zorder=3))
for cx in (-15, 0, 15):
    ax.add_patch(Polygon(stadium(cx, -34.37), closed=True, fc="#e8daef", ec="#7d3c98", lw=1.1, zorder=4))
ax.text(0, -34.37, "AA×3", ha="center", va="center", fontsize=8.5, color="#7d3c98", zorder=5)
ax.text(0, -57.5, "電源基板 52.5 × 58.0", ha="center", fontsize=8, color="#935116", zorder=5)

# Fly at relocated position: real board outline translated to (38,-50.14)
for pts in G["fly_edges"]:
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color="#145a32", lw=0.5, alpha=0.9, zorder=4)
ax.add_patch(Rectangle((38 - 11.79, -50.14 - 4.15), 23.57, 8.30, fc="#82e0aa", ec="none", alpha=0.35, zorder=3))
ax.text(38, -50.14, "Fly", ha="center", va="center", fontsize=7.5, color="#145a32", zorder=5)
ax.annotate("USB開口（北ゲーブル壁）", xy=(38, -62.5), xytext=(66, -70),
            fontsize=8, color="#145a32",
            arrowprops=dict(arrowstyle="-", color="#145a32", lw=0.8))

# trackpad island (real circle, D-053)
ax.add_patch(Circle((0, 48), 22, fc="#f9e79f", ec="#7d6608", lw=1.0, alpha=0.65, zorder=2))
ax.text(0, 48, "島 Ø44", ha="center", va="center", fontsize=8, color="#7d6608")

# FFC channel annotation
ax.annotate("FFCチャネル 11.5", xy=(30.5, -12), xytext=(86, 6), fontsize=8.5, color="#1a5276",
            arrowprops=dict(arrowstyle="-", color="#1a5276", lw=0.8))
ax.text(-155, 88, "実線=実ジオメトリ投影（ケース/基板/プレート）。ケース外形はトレイ実体の投影縁。",
        fontsize=8, color="#555")
fig.savefig(OUT + "case296b-topview-v2.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# ================= SECTIONS =================
fig, axes = plt.subplots(2, 1, figsize=(13.5, 8.6))
fig.suptitle("無線ケース Stage B 2D（実形状・断面図）", fontsize=12.5, weight="bold")

def draw_section(ax, secs, title, xlabel):
    for name, polys in secs.items():
        for p in polys:
            ax.add_patch(Polygon(p["outer"], closed=True, fc="#cfd8dc", ec="#455a64",
                                 lw=0.7, hatch="//", zorder=2))
            for w in p["inners"]:
                ax.add_patch(Polygon(w, closed=True, fc="white", ec="#455a64", lw=0.5, zorder=3))
    ax.axhline(22.00, color="#c0392b", lw=1.0, ls=(0, (6, 3)), zorder=5)
    ax.text(ax.get_xlim()[1] if False else 0, 23.2, "", fontsize=8)
    ax.set_title(title, fontsize=10.5, loc="left")
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel("ケースZ (mm)", fontsize=9)
    ax.set_aspect("equal"); ax.grid(True, lw=0.3, alpha=0.5)

# --- Section A: E-W at Y=-34.37 (through cell centres) ---
ax = axes[0]
draw_section(ax, G["secA"], "断面A：東西断面（Y=−34.37、セル中心を通る）", "X (mm)")
ax.set_xlim(-160, 160); ax.set_ylim(-6, 30)
# power board + cells + cover (Stage B stack)
ax.add_patch(Rectangle((-26.25, -0.65), 52.5, 0.8, fc="#f5b041", ec="#935116", lw=0.9, zorder=4))
for cx in (-15, 0, 15):
    ax.add_patch(Circle((cx, 7.40), 7.25, fc="#e8daef", ec="#7d3c98", lw=1.1, zorder=4))
ax.add_patch(Rectangle((-30.25, 15.15), 60.5, 1.5, fc="#aed6f1", ec="#1a5276", lw=1.0, zorder=4))
ax.add_patch(Rectangle((-30.25, 12.0), 2.0, 3.15, fc="#aed6f1", ec="#1a5276", lw=0.8, zorder=4))
ax.add_patch(Rectangle((28.25, 12.0), 2.0, 3.15, fc="#aed6f1", ec="#1a5276", lw=0.8, zorder=4))
ax.axhline(-0.65, xmin=0.40, xmax=0.60, color="#935116", lw=1.4, zorder=5)
ax.text(34, 17.6, "電池カバー上面 16.65（基準 22.00 まで 5.35）", fontsize=8.5, color="#1a5276")
ax.text(34, -3.5, "均し床 −0.65 ／ 電源基板 0.8", fontsize=8.5, color="#935116")
ax.text(120, 23.4, "キートップ基準 22.00", fontsize=8.5, color="#c0392b")

# --- Section B: N-S at X=0 (through bay, spine, island) ---
ax = axes[1]
draw_section(ax, G["secB"], "断面B：南北断面（X=0、ベイ〜中央棟〜島を通る）", "Y (mm)")
ax.set_xlim(-76, 92); ax.set_ylim(-6, 30)
ax.add_patch(Rectangle((-62.37, -0.65), 58.0, 0.8, fc="#f5b041", ec="#935116", lw=0.9, zorder=4))
ax.add_patch(Rectangle((-59.62, 0.15), 50.5, 14.5, fc="#e8daef", ec="#7d3c98", lw=1.1, zorder=4))
ax.text(-34.37, 7.4, "AAセル（軸方向断面）", ha="center", va="center", fontsize=8.5, color="#7d3c98")
ax.add_patch(Rectangle((-62.37, 15.15), 58.0, 1.5, fc="#aed6f1", ec="#1a5276", lw=1.0, zorder=4))
ax.add_patch(Rectangle((5.73, 4.65), 62.17, 1.2, fc="#aed6f1", ec="#1a5276", lw=0.9, zorder=4))
ax.text(30, 7.6, "Main基板", fontsize=8.5, color="#1a5276")
ax.text(-70, 17.6, "カバー上面 16.65", fontsize=8.5, color="#1a5276")
ax.text(60, 23.4, "基準 22.00", fontsize=8.5, color="#c0392b")
fig.tight_layout(rect=(0, 0, 1, 0.96))
fig.savefig(OUT + "case296b-sections-v2.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print("done")
