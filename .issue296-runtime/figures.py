"""Issue #296 2D approval figures. Frame: X centred (mm), Y from NEW north edge, +Y south.
Sources: outline 291x146.1 + south flat/peaks (south-notch study); D-060 tray;
trackpad centre asm (0,48) -> old-frame Y 112.4 -> new-frame 130.4 (D-053/#290 study);
Main ghost = preview.step body 8 bbox; Wing ghost = preview.step bodies 6/7 bbox."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle, Circle, FancyArrow
import matplotlib.patheffects as pe

font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
plt.rcParams["font.family"] = "Noto Sans CJK JP"

OUT = "/home/hatch/workspace/goals/he-piantor-42-keyboard-pmo/files/"
G = 18.0            # growth with C1 clearance correction (D-060 nominal 17)
DEPTH = 146.1 + G   # 164.1
TRAY_W, TRAY_D = 212.0, 17.6

# ---------------- Figure 1: top view ----------------
fig, ax = plt.subplots(figsize=(13.5, 8.2))
ax.set_aspect("equal"); ax.axis("off")
ax.set_xlim(-165, 165); ax.set_ylim(178, -14)

# new outline (south centre straightened to peak line)
ax.add_patch(Rectangle((-145.5, 0), 291, DEPTH, fill=False, lw=2.2, ec="#222"))
# old outline ghost
ax.add_patch(Rectangle((-145.5, G), 291, 146.1, fill=False, lw=0.9, ec="#999", ls=(0, (4, 3))))
ax.text(120, G + 4, "旧外形（点線）", fontsize=8, color="#666")

# tray band + field
ax.add_patch(Rectangle((-106, 0), TRAY_W, TRAY_D, fc="#fdeec9", ec="#b8860b", lw=1.6))
ax.add_patch(Rectangle((-104, 1.55), 208, 14.5, fill=False, lw=0.8, ec="#b8860b", ls=(0, (2, 2))))
# cells (starts from the C2 chain: gaps 0.75 + 1.5 + 1.5 + 1.5 + 0.75)
for x0 in (-103.25, -51.25, 0.75, 52.75):
    ax.add_patch(Rectangle((x0, 1.8), 50.5, 14.0, fc="#ffd98a", ec="#8a5a00", lw=1.1))
ax.text(0, 9.2, "単三 ×4（一列・上面剥き出し）", ha="center", va="center", fontsize=10.5, weight="bold")
# switch at east end
ax.add_patch(Rectangle((106.5, 4.5), 5.5, 8.0, fc="#c0392b", ec="#7b241c", lw=1.0))
ax.annotate("電源スイッチ\n（トレイ東端）", xy=(112, 8.5), xytext=(88, 30),
            fontsize=8.5, color="#7b241c",
            arrowprops=dict(arrowstyle="-", color="#7b241c", lw=0.8))
# band ends (receiver storage consideration)
ax.text(-126, 9, "帯端 39.5", ha="center", fontsize=8, color="#555")
ax.text(126, 9, "帯端 39.5", ha="center", fontsize=8, color="#555")

# Wing ghosts
for sx in (-1, 1):
    ax.add_patch(Rectangle((sx * 1.0 if sx > 0 else -142.24, G + 2.8), 141.24, 139.0,
                           fc="#eef3fa", ec="#7f9dbf", lw=0.7, zorder=0))
ax.text(-138, G + 12, "Wing基板（ゴースト）", fontsize=8, color="#5b7a9e")
ax.text(60, G + 12, "Wing基板", fontsize=8, color="#5b7a9e")
# Main ghost
ax.add_patch(Rectangle((-37.89, G + 66.7), 75.78, 65.6, fc="#e8f5e9", ec="#4e7a51", lw=1.0, zorder=1))
ax.text(0, G + 76, "Main基板（ゴースト）", ha="center", fontsize=8, color="#4e7a51")
# plate north / slope cover indication
ax.add_patch(Rectangle((-145.5, G + 1), 291, 9, fc="#d9d9d9", ec="none", alpha=0.55, zorder=0))
ax.text(-143, G + 6.5, "北スロープカバー帯", fontsize=8, color="#444")

# trackpad island
ax.add_patch(Circle((0, 130.4), 22, fc="#d7ecff", ec="#1a5276", lw=1.4, zorder=3))
ax.add_patch(Circle((0, 130.4), 20, fill=False, ec="#1a5276", lw=0.8, ls=(0, (2, 2)), zorder=3))
ax.annotate("トラックパッド島 Ø44\n（パッド Ø40・面 Z12.70）", xy=(16, 122), xytext=(52, 96),
            fontsize=9, color="#1a5276",
            arrowprops=dict(arrowstyle="-", color="#1a5276", lw=0.8))

# antenna band
ax.add_patch(Rectangle((-37.89, G + 132.3), 75.78, 13.8, fc="#f6ddf6", ec="#7d3c98", lw=0.9, hatch="///", zorder=1))
ax.annotate("アンテナ帯 13.8（PETG・金属不可）", xy=(30, G + 139), xytext=(58, G + 118),
            fontsize=8.5, color="#7d3c98",
            arrowprops=dict(arrowstyle="-", color="#7d3c98", lw=0.8))
# JBATT + cable route
ax.plot([100, 60, 24, 24], [10, 80, 146, G + 132.3], color="#c0392b", lw=1.1, ls=(0, (5, 3)), zorder=4)
ax.plot([24], [G + 132.3], marker="s", ms=5, color="#c0392b", zorder=5)
ax.annotate("電池ケーブル経路（約171mm）→ JBATT", xy=(26, G + 130), xytext=(-163, G + 96),
            fontsize=8.5, color="#c0392b",
            arrowprops=dict(arrowstyle="-", color="#c0392b", lw=0.8))
# south straight edge emphasis
ax.plot([-38.76, 38.76], [DEPTH, DEPTH], color="#222", lw=3.4)
ax.annotate("南辺：中央を直線化（凹みなし）", xy=(0, DEPTH), xytext=(-58, DEPTH + 9),
            fontsize=9, ha="center")

# dimensions
ax.annotate("", xy=(-145.5, -8), xytext=(145.5, -8), arrowprops=dict(arrowstyle="<->", lw=1.0))
ax.text(0, -11.5, "291", ha="center", fontsize=10)
ax.annotate("", xy=(-154, 0), xytext=(-154, DEPTH), arrowprops=dict(arrowstyle="<->", lw=1.0))
ax.text(-157, DEPTH / 2, "164.1（+18）", rotation=90, va="center", ha="center", fontsize=10)
ax.annotate("", xy=(-106, 21.5), xytext=(106, 21.5), arrowprops=dict(arrowstyle="<->", lw=0.9, color="#b8860b"))
ax.text(0, 25.5, "トレイ 212 × 17.6", ha="center", fontsize=9, color="#8a5a00")
ax.set_title("Issue #296 無線ケース 2D承認図 — 平面図（北トレイ D-060 / トラックパッド D-053 / 南辺直線化）",
             fontsize=12.5, pad=26)
fig.savefig(OUT + "case296-2d-topview.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# ---------------- Figure 2: cross sections ----------------
fig, (a1, a2) = plt.subplots(1, 2, figsize=(13.5, 5.6))
# Panel 1: N-S through tray (x: Y new-frame 0..30, y: Z)
a1.set_aspect("equal"); a1.set_xlim(-4, 34); a1.set_ylim(-1.5, 25)
a1.add_patch(Rectangle((0, 0), 30, 1.6, fc="#bbb", ec="#555"))                    # tray floor
a1.add_patch(Rectangle((2, 1.6), 17.6, 0.8, fc="#4e7a51", ec="#2e4d31"))          # power board (shown across band)
a1.add_patch(Circle((10.8, 9.65), 7.25, fc="#ffd98a", ec="#8a5a00", lw=1.4))       # cell section
a1.add_patch(Rectangle((0, 1.6), 2.0, 12.0, fc="#999", ec="#555"))                 # north wall (new)
a1.add_patch(Rectangle((19.6, 1.6), 2.6, 12.0, fc="#999", ec="#555"))              # existing north wall side
a1.plot([-4, 34], [22, 22], color="#c0392b", lw=1.0, ls=(0, (6, 3)))
a1.text(33.5, 22.6, "キートップ基準面 Z22.00", fontsize=8.5, color="#c0392b", ha="right")
a1.annotate("セル天面 Z16.90（基準面 −5.10）", xy=(10.8, 16.9), xytext=(13, 19.5),
            fontsize=9, arrowprops=dict(arrowstyle="-", lw=0.8))
a1.text(10.8, 9.65, "単三\nØ14.5", ha="center", va="center", fontsize=8.5)
a1.text(10.8, 0.7, "トレイ床（上面 Z1.60）", ha="center", fontsize=8)
a1.annotate("電源基板 0.8（床兼用）", xy=(6, 2.0), xytext=(14, 4.2), fontsize=8.5,
            arrowprops=dict(arrowstyle="-", lw=0.8))
a1.annotate("帯リム Z13.6（セル天面より −3.3）", xy=(20.9, 13.6), xytext=(21.5, 16.5),
            fontsize=8.5, color="#555", arrowprops=dict(arrowstyle="-", color="#555", lw=0.8))
a1.set_xlabel("北 ←　トレイ帯の南北断面（X=0）　→ 南（既存ケース側）", fontsize=9)
a1.set_ylabel("Z (mm)", fontsize=9); a1.grid(alpha=0.25, lw=0.4)
a1.set_title("断面A：電池トレイ（上面剥き出し・蓋なし）", fontsize=11)

# Panel 2: N-S through trackpad island (x: Y new-frame 100..165, y: Z)
a2.set_aspect("equal"); a2.set_xlim(98, 168); a2.set_ylim(-1.5, 25)
a2.add_patch(Rectangle((100, 4.7), 64, 1.2, fc="#a9c6a4", ec="#4e7a51"))          # Main board top zone
a2.plot([100, 108.4], [14.27, 12.7], color="#1a5276", lw=1.6)                     # shell S rim slope
a2.plot([108.4, 152.4], [12.7, 12.7], color="#1a5276", lw=2.2)                    # flattened island
a2.plot([152.4, 164], [12.7, 10.9], color="#1a5276", lw=1.6)                      # shell N rim
a2.add_patch(Rectangle((110.4, 7.3), 40, 5.4, fc="#d7ecff", ec="#1a5276", lw=0.9))  # pad module band
a2.plot([98, 168], [10.9, 10.9], color="#888", lw=0.9, ls=(0, (4, 3)))
a2.text(103, 8.2, "プレート上面 Z10.90", fontsize=8, color="#666", ha="left")
a2.plot([98, 168], [22, 22], color="#c0392b", lw=1.0, ls=(0, (6, 3)))
a2.text(167, 22.6, "Z22.00", fontsize=8.5, color="#c0392b", ha="right")
a2.annotate("平坦化した島 Ø44・面 Z12.70（増高ゼロ）", xy=(130.4, 12.7), xytext=(104, 18.5),
            fontsize=9, color="#1a5276", arrowprops=dict(arrowstyle="-", color="#1a5276", lw=0.8))
a2.text(130.4, 9.6, "パッドモジュール帯 Z7.3–12.7", ha="center", fontsize=8, color="#1a5276")
a2.annotate("", xy=(108.4, 27.5), xytext=(152.4, 27.5), arrowprops=dict(arrowstyle="<->", lw=0.9))
a2.set_xlabel("北 ←　中央ベイ南北断面（X=0）　→ 南", fontsize=9)
a2.set_ylabel("Z (mm)", fontsize=9); a2.grid(alpha=0.25, lw=0.4)
a2.set_title("断面B：トラックパッド島（D-053）", fontsize=11)
fig.savefig(OUT + "case296-2d-sections.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print("figures written")
