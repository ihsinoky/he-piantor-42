"""Backend-independent source for Wing placement/net exports and JITX assembly.

mm, board center origin, +Y up, top-side, CCW degrees.
Representative geometry uses the attributed Piantor evaluation snapshot.
"""

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

INTERFACE = (
    "HALL_5V",
    "GND",
    "MUX_A0",
    "GND",
    "MUX_A1",
    "MUX_A2",
    "WING_EN",
    "GND",
    "MUX_OUT_A",
    "GND",
    "MUX_OUT_B",
    "GND",
    "MUX_OUT_C",
    "GND",
)
HALL_PINS = {"VCC": "1", "OUT": "2", "GND": "3"}
MUX_PINS = dict(
    zip(
        (
            "A0",
            "EN",
            "NC",
            "S1",
            "S2",
            "S3",
            "S4",
            "D",
            "S8",
            "S7",
            "S6",
            "S5",
            "VDD",
            "GND",
            "A2",
            "A1",
        ),
        map(str, range(1, 17)),
        strict=True,
    )
)


@dataclass
class Part:
    reference: str
    kind: str
    mpn: str
    x_mm: float
    y_mm: float
    pins: dict[str, str | None]  # physical pin -> net; None means intentional NC
    rotation_ccw_deg: float = 0
    side: str = "top"
    value: str = ""


def define_wing(pitch: float, kind: str = "pitch9") -> dict:
    if not math.isfinite(pitch) or not 16 <= pitch <= 17:
        raise ValueError("Wing pitch must be finite and in [16, 17] mm")
    if kind not in ("pitch9", "representative21", "load21"):
        raise ValueError(f"Unknown Wing kind: {kind}")
    parts: list[Part] = []
    sensors = []
    groups: dict[str, list[tuple[float, float, str]]] = {g: [] for g in "ABC"}
    if kind == "representative21":
        # Exact repository Piantor tuples; only pitch, Y reflection and translation.
        layout = json.loads(Path(__file__).with_name("piantor_left21.json").read_text())
        keys = layout["keys"]
        min_x, max_x = min(k["x"] for k in keys), max(k["x"] for k in keys)
        min_y, max_y = min(k["y"] for k in keys), max(k["y"] for k in keys)
        # One-pitch key cells, 3 mm border and 18 mm service strip below the cells.
        width = (max_x - min_x + 1) * pitch + 6
        height = (max_y - min_y + 1) * pitch + 6 + 18
        for i, key in enumerate(keys):
            x = (key["x"] - (min_x + max_x) / 2) * pitch
            y = ((min_y + max_y) / 2 - key["y"]) * pitch + 9
            groups["ABC"[i % 3]].append((x, y, "key"))
        mux_sites = [(x, -height / 2 + 10) for x in (0.0, 14.0, 28.0)]
        connector = (-width / 2 + 18, -height / 2 + 10)
    else:
        # Column A/B/C, row/address 0/1/2, identical pitch-only and load coverage.
        for c, group in enumerate("ABC"):
            groups[group] = [((c - 1) * pitch, (1 - r) * pitch + 10, "key") for r in range(3)]
            if kind == "load21":
                groups[group] += [((c - 1) * pitch, -15 - 5 * r, "load") for r in range(4)]
        width, height = (64.0, 80.0) if kind == "pitch9" else (98.0, 98.0)
        mux_sites = [(-18.0, -22.0), (0.0, -22.0), (18.0, -22.0)]
        connector = (0.0, -33.0)
        if kind == "load21":
            mux_sites = [(30.0, -12.0), (30.0, -24.0), (30.0, -36.0)]
            connector = (-29.0, -39.0)

    def add(ref, component_kind, mpn, x, y, pins, value=""):
        parts.append(Part(ref, component_kind, mpn, x, y, pins, value=value))

    def probe(ref, net, x, y):
        add(ref, "testpoint", "PCB_PAD_1.2MM", x, y, {"1": net})

    def capacitor(ref, x, y):
        add(
            ref,
            "capacitor",
            "GRM188R71C104KA01D",
            x,
            y,
            {"1": "HALL_5V", "2": "GND"},
            "100nF 16V X7R +/-10% 0603",
        )

    for group, (mx, my) in zip("ABC", mux_sites, strict=True):
        pins = {pin: None for pin in MUX_PINS.values()}
        for port, net in {
            "VDD": "HALL_5V",
            "GND": "GND",
            "EN": "WING_EN",
            "D": f"MUX_OUT_{group}",
            **{f"A{i}": f"MUX_A{i}" for i in range(3)},
        }.items():
            pins[MUX_PINS[port]] = net
        for address, (x, y, role) in enumerate(groups[group]):
            ref = f"U_H{group}{address}"
            raw = f"H_{group}{address}_RAW"
            add(ref, "hall", "DRV5055A3QDBZR", x, y, {"1": "HALL_5V", "2": raw, "3": "GND"})
            capacitor(f"C_H{group}{address}", x + 3.5, y)
            pins[MUX_PINS[f"S{address + 1}"]] = raw
            sensors.append(
                {
                    "reference": ref,
                    "mux": f"U_MUX_{group}",
                    "address": address,
                    "role": role,
                    "x_mm": x,
                    "y_mm": y,
                }
            )
        add(f"U_MUX_{group}", "mux", "TMUX1208PWR", mx, my, pins)
        capacitor(f"C_MUX_{group}", mx + 5, my + 1)
        probe(f"TP_W_MUX{group}", f"MUX_OUT_{group}", mx, my - 5)
        probe(f"TP_W_GND_{group}", "GND", mx + 3, my - 5)
    add(
        "J_WING",
        "connector",
        "BM14B-GHS-TBT(LF)(SN)",
        *connector,
        {**{str(i): n for i, n in enumerate(INTERFACE, 1)}, "MP": None},
    )

    # Representative raw nodes: center / orthogonal / diagonal for the 3x3 field.
    raw_refs = ("B1", "B0", "A0")
    if kind == "representative21":
        raw_refs = ("A2", "B2", "C0")
    for suffix, channel in zip(("CTR", "N", "DIAG"), raw_refs, strict=True):
        sensor = next(s for s in sensors if s["reference"] == f"U_H{channel}")
        probe(f"TP_H_{suffix}_RAW", f"H_{channel}_RAW", sensor["x_mm"] - 3.5, sensor["y_mm"])
    # Rail/control access row; no extra connector signals or remote pull-downs.
    ty = 37.0 if kind == "pitch9" else 45.0
    if kind == "representative21":
        ty = height / 2 - 3
    for i, net in enumerate(("HALL_5V", "GND", "MUX_A0", "MUX_A1", "MUX_A2", "WING_EN")):
        label = {"HALL_5V": "H5V", "GND": "GND", "WING_EN": "EN"}.get(net, net[-2:])
        probe(f"TP_W_{label}", net, -10 + 4 * i, ty)

    nets: dict[str, list[str]] = {}
    ncs = []
    for part in parts:
        for pin, net in part.pins.items():
            endpoint = f"{part.reference}.{pin}"
            if net is None:
                ncs.append(endpoint)
            else:
                nets.setdefault(net, []).append(endpoint)
    geometry = {}
    if kind == "representative21":
        for i, key in enumerate(keys):
            sensor = next(s for s in sensors if s["reference"] == f"U_H{'ABC'[i % 3]}{i // 3}")
            sensor.update(source_key_id=key["id"], source_x_u=key["x"], source_y_u=key["y"])
        geometry = {
            "layout_source": layout,
            "layout_transform": "x=(source_x-2.75)*pitch; y=(1.875-source_y)*pitch+9; no rotation",
            "key_cell_bounds_mm": [-width / 2 + 3, -height / 2 + 21, width / 2 - 3, height / 2 - 3],
            "outline_policy": "one-pitch cells; 3 mm border; 18 mm bottom service strip; no compression",
            "size_requirement": {
                "limit_mm": [100, 100],
                "fits": width <= 100 and height <= 100,
                "excess_mm": [max(0, width - 100), max(0, height - 100)],
                "decision": "PO: revise 100x100 requirement or explicitly revise Piantor layout; do not compress",
            },
        }
    return {
        **geometry,
        "schema_version": 1,
        "name": f"{kind}-{pitch:g}mm",
        "kind": kind,
        "pitch_mm": pitch,
        "frame": "mm; board-center; +Y up; top; CCW",
        "outline_mm": [
            [-width / 2, -height / 2],
            [width / 2, -height / 2],
            [width / 2, height / 2],
            [-width / 2, height / 2],
        ],
        "width_mm": width,
        "height_mm": height,
        "layers": 2,
        "thickness_mm": 1.2,
        "mounting_holes": [
            {"x_mm": x, "y_mm": y, "diameter_mm": 2.2, "keepout_diameter_mm": 5.0}
            for x in (-width / 2 + 3, width / 2 - 3)
            for y in (-height / 2 + 3, height / 2 - 3)
        ],
        "harness": {"length_mm": 100, "wiring": "1:1", "conductors": 14},
        "connector_cable_access_mm": [
            connector[0] - 13,
            connector[1] - 7,
            connector[0] + 13,
            connector[1] + 1,
        ],
        "sensor_sites": sensors,
        "components": [asdict(p) for p in parts],
        "nets": dict(sorted(nets.items())),
        "intentional_nc": sorted(ncs),
        "key_cell_assumption_mm": pitch,
        "status": "placement/net input; unrouted; mechanics and fab not qualified",
    }
