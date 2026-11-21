#!/usr/bin/env python3
"""Measure In1.Cu Gerber zone-fill coverage of the F1 target annuli and the
JSWD guide-hole disks. Parses the G36 region (the GND plane fill) from a
KiCad-exported RS-274X file (format 4.6).
Usage: fix1_gerber_check.py <wmain-In1_Cu.g1>
"""
import sys, re, json
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

def parse_regions(path):
    text = open(path).read()
    regions = []
    for m in re.finditer(r"G36\*(.*?)G37\*", text, re.S):
        body = m.group(1)
        pts = []
        for tok in re.finditer(r"X(-?\d+)Y(-?\d+)D0[12]\*", body):
            # KiCad Gerber Y is negated relative to board coordinates
            pts.append((int(tok.group(1)) / 1e6, -int(tok.group(2)) / 1e6))
        if len(pts) >= 3:
            p = Polygon(pts)
            if not p.is_valid:
                p = p.buffer(0)
            regions.append(p)
    return unary_union(regions) if regions else None

def main():
    region = parse_regions(sys.argv[1])
    print("region area mm2:", None if region is None else round(region.area, 6))
    targets = [
        ("RESET_N", 112.9, 133.75, 0.6, 0.3),
        ("RESET_N", 108.3, 133.975, 0.45, 0.3),
        ("SYS_3V3", 100.5, 134.95, 0.6, 0.3),
    ]
    out = []
    for net, x, y, dia, drill in targets:
        ann = Point(x, y).buffer(dia / 2, resolution=256).difference(
            Point(x, y).buffer(drill / 2, resolution=256))
        out.append({"net": net, "x": x, "y": y,
                    "gerber_fill_overlap_mm2": round(ann.intersection(region).area, 6)})
    holes = [(106.691058, 136.079763), (114.285006, 134.884519), (114.332879, 136.915955)]
    hout = []
    for x, y in holes:
        disk = Point(x, y).buffer(0.9906 / 2, resolution=256)
        hout.append({"x": x, "y": y,
                     "gerber_fill_overlap_mm2": round(disk.intersection(region).area, 6)})
    print(json.dumps({"annuli": out, "guide_holes": hout}, indent=1))

if __name__ == "__main__":
    main()
