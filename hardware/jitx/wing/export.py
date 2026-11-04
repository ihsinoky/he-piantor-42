"""Deterministic placement/net/BOM review exports; not manufacturing outputs."""

import argparse
import csv
import io
import json
from collections import defaultdict
from pathlib import Path

from wing.definition import define_wing


def csv_text(fields, rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def render_svg(spec):
    w, h = spec["width_mm"], spec["height_mm"]
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-w / 2 - 3} {-h / 2 - 8} {w + 6} {h + 15}">',
        "<style>text{font-family:monospace;font-size:1.7px} .cell{fill:none;stroke:#aab;stroke-width:.2}</style>",
        f'<rect x="{-w / 2}" y="{-h / 2}" width="{w}" height="{h}" fill="#eef9ef" stroke="#263" stroke-width=".3"/>',
        f'<text x="{-w / 2}" y="{-h / 2 - 3}">{spec["name"]} / {w:g} x {h:g} mm / UNROUTED</text>',
    ]
    for sensor in spec["sensor_sites"]:
        if sensor["role"] == "key":
            x, y, p = sensor["x_mm"], sensor["y_mm"], spec["pitch_mm"]
            lines.append(
                f'<rect class="cell" x="{x - p / 2}" y="{-y - p / 2}" width="{p}" height="{p}"/>'
            )
    x1, y1, x2, y2 = spec["connector_cable_access_mm"]
    lines.append(
        f'<rect x="{x1}" y="{-y2}" width="{x2 - x1}" height="{y2 - y1}" fill="#ddf" opacity=".7"/>'
    )
    for hole in spec["mounting_holes"]:
        lines.append(
            f'<circle cx="{hole["x_mm"]}" cy="{-hole["y_mm"]}" r="2.5" fill="none" stroke="#888" stroke-width=".2"/>'
        )
        lines.append(
            f'<circle cx="{hole["x_mm"]}" cy="{-hole["y_mm"]}" r="1.1" fill="white" stroke="#444" stroke-width=".2"/>'
        )
    sizes = {
        "hall": (3, 3),
        "mux": (7.4, 6),
        "capacitor": (2.5, 1.3),
        "testpoint": (1.2, 1.2),
        "connector": (20.95, 5.6),
    }
    colors = {
        "hall": "#a33",
        "mux": "#333",
        "capacitor": "#ba7",
        "testpoint": "#d90",
        "connector": "#268",
    }
    for row in spec["components"]:
        x, y = row["x_mm"], row["y_mm"]
        rw, rh = sizes[row["kind"]]
        if row["kind"] == "connector":
            y -= 2
        lines.append(
            f'<rect x="{x - rw / 2}" y="{-y - rh / 2}" width="{rw}" height="{rh}" fill="{colors[row["kind"]]}"/>'
        )
        if row["kind"] in ("hall", "mux", "connector"):
            lines.append(
                f'<text x="{x - rw / 2}" y="{-y - rh / 2 - 0.6}">{row["reference"]}</text>'
            )
    lines += [
        f'<text x="{-w / 2}" y="{h / 2 + 4}">cells = pitch assumption; cable = reserved projection; no switch CAD</text>',
        "</svg>",
    ]
    return "\n".join(lines) + "\n"


def artifacts(spec):
    rows = spec["components"]
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["kind"], row["mpn"], row["value"])].append(row["reference"])
    return {
        "definition.json": json.dumps(spec, ensure_ascii=False, indent=2) + "\n",
        "placements.csv": csv_text(
            ["reference", "mpn", "x_mm", "y_mm", "rotation_ccw_deg", "side"],
            [
                {
                    f: row[f]
                    for f in ("reference", "mpn", "x_mm", "y_mm", "rotation_ccw_deg", "side")
                }
                for row in rows
            ],
        ),
        "bom.csv": csv_text(
            ["kind", "mpn", "value", "quantity", "references"],
            [
                {
                    "kind": k,
                    "mpn": m,
                    "value": v,
                    "quantity": len(refs),
                    "references": " ".join(refs),
                }
                for (k, m, v), refs in sorted(grouped.items())
            ],
        ),
        "nets.csv": csv_text(
            ["net", "reference", "physical_pin"],
            [
                {
                    "net": net,
                    "reference": endpoint.rsplit(".", 1)[0],
                    "physical_pin": endpoint.rsplit(".", 1)[1],
                }
                for net, members in spec["nets"].items()
                for endpoint in members
            ]
            + [
                {"net": "NC", "reference": e.rsplit(".", 1)[0], "physical_pin": e.rsplit(".", 1)[1]}
                for e in spec["intentional_nc"]
            ],
        ),
        "placement.svg": render_svg(spec),
    }


def export_all(output, check=False):
    for kind in ("pitch9", "representative21", "load21"):
        for pitch in (16.0, 17.0):
            spec = define_wing(pitch, kind)
            directory = output / spec["name"]
            for name, content in artifacts(spec).items():
                target = directory / name
                if check:
                    if not target.is_file() or target.read_text() != content:
                        raise ValueError(f"Missing or stale artifact: {target}")
                else:
                    directory.mkdir(parents=True, exist_ok=True)
                    target.write_text(content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("wing/generated"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    export_all(args.output, args.check)
