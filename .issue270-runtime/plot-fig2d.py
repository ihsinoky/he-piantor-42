import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPoly

data = json.loads(open("figdata-2d.json").read())
fig, axes = plt.subplots(1, 2, figsize=(13, 6.5))
panels = [("17mm-left", (-54, 0), "LEFT (J2 side) - simplified notch (2d) vs exact-offset notch (2b)"),
          ("17mm-right", (0, 54), "RIGHT (J3 side) - simplified notch (2d) vs exact-offset notch (2b)")]
seamloc = {"17mm-left": (-29.92, 52.11), "17mm-right": (18.45, 32.64)}
for ax, (var, xr, title) in zip(axes, panels):
    ax.add_patch(MplPoly(data["main"], closed=True, facecolor="#f2c94c", edgecolor="#8a6d00", lw=1.2, alpha=0.55, zorder=1))
    for key, style, lw, color, label, z in (
            (var + "-rev5", ":", 0.9, "#999999", "Wing Rev.5 outline (pre-notch)", 2),
            (var + "-2b", "--", 1.1, "#c0392b", "Wing Rev.6 2b notch (exact 0.55 offset)", 3),
            (var + "-2d", "-", 1.8, "#1f5fa6", "Wing Rev.6 2d notch (simplified, RF 0.55)", 4)):
        pts = data[key]
        xs = [q[0] for q in pts] + [pts[0][0]]; ys = [q[1] for q in pts] + [pts[0][1]]
        ax.plot(xs, ys, style, color=color, lw=lw, label=label, zorder=z)
    sx, sy = seamloc[var]
    ax.plot([sx], [sy], marker="o", ms=7, mfc="none", mec="#c0392b", mew=1.8, zorder=5)
    ax.annotate("seam min 0.56 mm", (sx, sy), textcoords="offset points", xytext=(8, 10),
                fontsize=9, color="#c0392b", zorder=5)
    ax.set_xlim(*xr); ax.set_ylim(22, 64); ax.set_aspect("equal")
    ax.set_title(title, fontsize=10.5)
    ax.set_xlabel("case frame X [mm]"); ax.set_ylabel("case frame Y [mm]")
    ax.grid(True, lw=0.3, alpha=0.4)
    ax.legend(fontsize=8, loc="lower left")
    ax.text(0.02, 0.96, "gold = Main Rev.9 final outline (tab)", transform=ax.transAxes, fontsize=8.5, va="top")
fig.tight_layout()
fig.savefig("fig-2d-wing-notch.png", dpi=170)
print("saved fig-2d-wing-notch.png")
