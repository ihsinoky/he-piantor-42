#!/usr/bin/env python3
"""Generate transformed key-center coordinates and SVG preview.

Coordinate convention:
- Source x/y come from QMK Cantor LAYOUT_split_3x6_3 in key units.
- +x is right, +y is down.
- Left pivot is the inner home-row key center at (5, 1.25) u.
- Right pivot is the inner home-row key center at (8, 1.25) u.
- Baseline rotations are +30 deg left and -30 deg right.
- The inner-home center-to-center gap is a separate tunable parameter.
"""
import csv, json, math
from pathlib import Path

HERE=Path(__file__).resolve().parent
src=json.loads((HERE/"layout_source.json").read_text(encoding="utf-8"))
p=src["parameters"]
pitch=float(p["pitch_mm"])
gap=float(p["inner_home_center_gap_mm"])

def transform(k):
    left=k["side"]=="L"
    pivot=p["pivot_left"] if left else p["pivot_right"]
    deg=float(p["left_rotation_deg"] if left else p["right_rotation_deg"])
    dx=(float(k["x"])-float(pivot["x_u"]))*pitch
    dy=(float(k["y"])-float(pivot["y_u"]))*pitch
    a=math.radians(deg)
    xr=dx*math.cos(a)-dy*math.sin(a)
    yr=dx*math.sin(a)+dy*math.cos(a)
    return dict(k,
        x_mm=(-gap/2 if left else gap/2)+xr,
        y_mm=yr,
        rotation_deg=deg)

keys=[transform(k) for k in src["keys"]]
with (HERE/"key_positions.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.writer(f,lineterminator="\n"); w.writerow(["id","side","source_x_u","source_y_u","x_mm","y_mm","rotation_deg"])
    for k in keys:
        w.writerow([k["id"],k["side"],k["x"],k["y"],f'{k["x_mm"]:.4f}',f'{k["y_mm"]:.4f}',f'{k["rotation_deg"]:.1f}'])

minx=min(k["x_mm"] for k in keys)-12; maxx=max(k["x_mm"] for k in keys)+12
miny=min(k["y_mm"] for k in keys)-12; maxy=max(k["y_mm"] for k in keys)+12
W=maxx-minx; H=maxy-miny
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.1f}mm" height="{H:.1f}mm" viewBox="0 0 {W:.3f} {H:.3f}">',
'<style>rect{fill:#e8eef5;stroke:#263240;stroke-width:.7}circle{fill:#f85149}.axis{stroke:#79c0ff;stroke-width:.5;stroke-dasharray:2 2}.txt{font:4px sans-serif;fill:#93a1af}</style>',
f'<rect x="0" y="0" width="{W:.3f}" height="{H:.3f}" fill="#0b0f14"/>']
for k in keys:
    cx=k["x_mm"]-minx; cy=k["y_mm"]-miny
    parts.append(f'<g transform="rotate({k["rotation_deg"]} {cx:.3f} {cy:.3f})"><rect x="{cx-8.25:.3f}" y="{cy-8.25:.3f}" width="16.5" height="16.5" rx="1.5"/><circle cx="{cx:.3f}" cy="{cy:.3f}" r="1.2"/></g>')
parts.append(f'<text class="txt" x="5" y="{H-5:.3f}">pitch {pitch:.1f} mm / gap {gap:.1f} mm / L {p["left_rotation_deg"]} deg / R {p["right_rotation_deg"]} deg</text>')
parts.append("</svg>")
(HERE/"layout_preview.svg").write_text("\n".join(parts),encoding="utf-8")
