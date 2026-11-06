"""Issue #178: one M1 board, two nine-key pitch fields, shared column MUXes.

Same component geometry, pin numbering and GH14 interface as pitch9. Millimetres,
board-centred, +Y up. This definition is also the native KiCad input source.
"""

from copy import deepcopy

from wing.definition import INTERFACE, MUX_PINS, define_wing


def define_m1_matrix():
    base = deepcopy(define_wing(16))
    parts = [
        p
        for p in base["components"]
        if p["kind"] not in ("hall",) and not p["reference"].startswith(("C_H", "TP_H_"))
    ]
    sensors = []
    for pitch, cx, offset in ((16, -34, 0), (17, 34, 3)):
        field = define_wing(pitch)
        for part in field["components"]:
            if part["kind"] != "hall" and not part["reference"].startswith(("C_H", "TP_H_")):
                continue
            part = deepcopy(part)
            part["x_mm"] += cx
            if part["kind"] == "testpoint":
                part["reference"] = part["reference"].replace("TP_H_", f"TP_H{pitch}_")
            else:
                part["reference"] = part["reference"][:-1] + str(
                    int(part["reference"][-1]) + offset
                )
            for pin, net in part["pins"].items():
                if net and net.startswith("H_") and net.endswith("_RAW"):
                    part["pins"][pin] = net[:3] + str(int(net[3]) + offset) + net[4:]
            parts.append(part)
        for sensor in field["sensor_sites"]:
            s = deepcopy(sensor)
            s.update(
                reference=s["reference"][:-1] + str(s["address"] + offset),
                address=s["address"] + offset,
                x_mm=s["x_mm"] + cx,
                block_pitch_mm=pitch,
                column=s["mux"][-1],
                row=s["address"],
            )
            sensors.append(s)
    for group in "ABC":
        mux = next(p for p in parts if p["reference"] == f"U_MUX_{group}")
        for address in range(6):
            mux["pins"][MUX_PINS[f"S{address + 1}"]] = f"H_{group}{address}_RAW"
    nets, ncs = {}, []
    for part in parts:
        for pin, net in part["pins"].items():
            endpoint = f"{part['reference']}.{pin}"
            if net is None:
                ncs.append(endpoint)
            else:
                nets.setdefault(net, []).append(endpoint)
    width, height = 128, 80
    base.update(
        name="m1-matrix18-16-17mm",
        kind="matrix18",
        pitch_mm=None,
        blocks=[
            {
                "pitch_mm": p,
                "center_x_mm": c,
                "center_y_mm": 10,
                "columns": 3,
                "rows": 3,
                "addresses": list(range(a, a + 3)),
            }
            for p, c, a in ((16, -34, 0), (17, 34, 3))
        ],
        width_mm=width,
        height_mm=height,
        outline_mm=[[-64, -40], [64, -40], [64, 40], [-64, 40]],
        mounting_holes=[
            {"x_mm": x, "y_mm": y, "diameter_mm": 2.2, "keepout_diameter_mm": 5}
            for x in (-61, 61)
            for y in (-37, 37)
        ],
        components=parts,
        sensor_sites=sensors,
        nets=dict(sorted(nets.items())),
        intentional_nc=sorted(ncs),
        key_cell_assumption_mm=[16, 17],
        minimum_interblock_key_center_distance_target_mm=34,
        status="design input; see Issue 178 qualification evidence for routed state",
    )
    assert next(p for p in parts if p["reference"] == "J_WING")["pins"] == {
        **{str(i): n for i, n in enumerate(INTERFACE, 1)},
        "MP": None,
    }
    return base
