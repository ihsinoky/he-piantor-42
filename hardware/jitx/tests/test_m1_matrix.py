"""M1 pitch fields, full pin path, physical separations and input reproducibility."""

import math
from collections import Counter
from pathlib import Path

from jitx.sample import SampleSubstrate
from jitx.substrate import SubstrateContext
from jitx.test import TestCase

from he_piantor_42_jitx.evaluation_wing import M1MatrixCircuit
from wing.definition import INTERFACE
from wing.export import export_all
from wing.matrix import define_m1_matrix


class M1MatrixTest(TestCase):
    def test_blocks_and_nearest_distance(self):
        spec = define_m1_matrix()
        sensors = spec["sensor_sites"]
        self.assertEqual(Counter(s["block_pitch_mm"] for s in sensors), {16: 9, 17: 9})
        for pitch in (16, 17):
            block = [s for s in sensors if s["block_pitch_mm"] == pitch]
            self.assertEqual(len({s["reference"] for s in block}), 9)
            for a in block:
                for b in block:
                    self.assertEqual(
                        a["x_mm"] - b["x_mm"], (ord(a["column"]) - ord(b["column"])) * pitch
                    )
                    self.assertEqual(a["y_mm"] - b["y_mm"], (b["row"] - a["row"]) * pitch)
                    self.assertEqual(a["address"], a["row"] + (0 if pitch == 16 else 3))
        nearest = min(
            math.dist((a["x_mm"], a["y_mm"]), (b["x_mm"], b["y_mm"]))
            for a in sensors
            for b in sensors
            if a["block_pitch_mm"] != b["block_pitch_mm"]
        )
        self.assertEqual(nearest, 35)
        self.assertGreaterEqual(nearest, 34)
        self.assertEqual(
            Counter(p["kind"] for p in spec["components"]),
            {"hall": 18, "capacitor": 21, "mux": 3, "connector": 1, "testpoint": 18},
        )
        export_all(Path(__file__).resolve().parents[1] / "wing/generated", check=True)

    def test_native_complete_pin_paths(self):
        spec = define_m1_matrix()
        with SubstrateContext(SampleSubstrate()):
            c = M1MatrixCircuit()
            for i, net in enumerate(INTERFACE):
                self.assertIn(c.J_WING.p[i], getattr(c, net))
            for group in "ABC":
                mux = getattr(c, f"U_MUX_{group}")
                for port, net in (
                    ("VDD", "HALL_5V"),
                    ("GND", "GND"),
                    ("EN", "WING_EN"),
                    ("D", f"MUX_OUT_{group}"),
                    *((f"A{i}", f"MUX_A{i}") for i in range(3)),
                ):
                    self.assertIn(getattr(mux, port), getattr(c, net))
                for address in range(6):
                    raw = getattr(c, f"H_{group}{address}_RAW")
                    hall = getattr(c, f"U_H{group}{address}")
                    self.assertIn(hall.OUT, raw)
                    self.assertIn(getattr(mux, f"S{address + 1}"), raw)
                    self.assertIn(hall.VCC, c.HALL_5V)
                    self.assertIn(hall.GND, c.GND)
                for port in ("S7", "S8", "NC"):
                    for net in spec["nets"]:
                        self.assertNotIn(getattr(mux, port), getattr(c, net))
