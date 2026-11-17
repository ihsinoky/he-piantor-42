import json, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
D = json.load(open("/home/hatch/workspace/projects/he-piantor-wingnotch/.issue273-runtime/dbg2.json"))
fig, axes = plt.subplots(1, 2, figsize=(15, 7))
for ax, variant in zip(axes, ("17mm-left", "17mm-right")):
    v = D["variants"][variant]
    for key, style, lab in (("rev5", "grey", "Rev.5"), ("rev6", "b-", "Rev.6-2d")):
        xs = [c[0] for c in v[key]]; ys = [c[1] for c in v[key]]
        ax.plot(xs, ys, style, lw=1.0, label=lab)
    xs = [c[0] for c in D["main"]]; ys = [c[1] for c in D["main"]]
    ax.plot(xs, ys, "k-", lw=1.2, label="Main Rev.9")
    for e in v["chain"]:
        if e[0] == "line":
            ax.plot([e[1][0], e[2][0]], [e[1][1], e[2][1]], "r--", lw=1.0)
        else:
            _, O, r, a, bb, _m = e
            a0 = math.atan2(a[1] - O[1], a[0] - O[0]); a1 = math.atan2(bb[1] - O[1], bb[0] - O[0])
            while a1 - a0 > math.pi: a1 -= 2 * math.pi
            while a1 - a0 < -math.pi: a1 += 2 * math.pi
            th = [a0 + (a1 - a0) * i / 40 for i in range(41)]
            ax.plot([O[0] + r * math.cos(t) for t in th],
                    [O[1] + r * math.sin(t) for t in th], "r--", lw=1.0)
    ax.set_aspect("equal"); ax.grid(True, lw=0.3); ax.set_title(variant)
    if "left" in variant:
        ax.set_xlim(-45, -5)
    else:
        ax.set_xlim(5, 45)
    ax.set_ylim(25, 60); ax.legend(loc="best", fontsize=8)
fig.tight_layout()
fig.savefig("/home/hatch/workspace/projects/he-piantor-wingnotch/.issue273-runtime/dbg-notch.png", dpi=110)
print("saved")
