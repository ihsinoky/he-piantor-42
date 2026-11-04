"""Frozen interface, native connectivity, geometry, and reproducible Wing inputs."""

import json
import math
from collections import Counter
from pathlib import Path

from jitx.component import Component
from jitx.inspect import visit
from jitx.landpattern import Pad, PadShape
from jitx.sample import SampleSubstrate
from jitx.substrate import SubstrateContext
from jitx.test import TestCase
from shapely.geometry import Point, box
from shapely.wkt import loads

from he_piantor_42_jitx.evaluation_wing import wing_circuit
from wing.definition import define_wing
from wing.export import export_all

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_INTERFACE = (
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


class EvaluationWingTest(TestCase):
    def test_native_interface_and_full_load(self):
        for kind in ("pitch9", "representative21", "load21"):
            for pitch in (16.0, 17.0):
                with self.subTest(kind=kind, pitch=pitch), SubstrateContext(SampleSubstrate()):
                    c = wing_circuit(pitch, kind)
                    for i, net in enumerate(EXPECTED_INTERFACE):
                        self.assertIn(c.J_WING.p[i], getattr(c, net))
                    # Real native MUX/Hall ports, not just JSON pin labels.
                    used = 3 if kind == "pitch9" else 7
                    for group in "ABC":
                        mux = getattr(c, f"U_MUX_{group}")
                        self.assertIn(mux.EN, c.WING_EN)
                        self.assertIn(mux.VDD, c.HALL_5V)
                        self.assertIn(mux.GND, c.GND)
                        self.assertIn(mux.D, getattr(c, f"MUX_OUT_{group}"))
                        for address in range(used):
                            raw = getattr(c, f"H_{group}{address}_RAW")
                            hall = getattr(c, f"U_H{group}{address}")
                            self.assertIn(hall.OUT, raw)
                            self.assertIn(getattr(mux, f"S{address + 1}"), raw)
                            self.assertIn(hall.VCC, c.HALL_5V)
                            self.assertIn(hall.GND, c.GND)
                            cap = getattr(c, f"C_H{group}{address}")
                            self.assertIn(cap.p1, c.HALL_5V)
                            self.assertIn(cap.p2, c.GND)
                        for address in range(used + 1, 9):
                            port = getattr(mux, f"S{address}")
                            for name in define_wing(pitch, kind)["nets"]:
                                self.assertNotIn(port, getattr(c, name))
                    self.assertEqual(len(list(visit(c, Component))), 40 if kind == "pitch9" else 64)
                    self.assertEqual(len(c.J_WING.landpattern.contacts), 14)
                    self.assertEqual(len(c.J_WING.landpattern.reinforcement), 2)
                    self.assertAlmostEqual(
                        c.J_WING.landpattern.contacts[0].transform.translation[0], 8.125
                    )

    def test_native_copper_placement_bounds_holes_and_overlaps(self):
        for kind in ("pitch9", "representative21", "load21"):
            for pitch in (16.0, 17.0):
                with self.subTest(kind=kind, pitch=pitch), SubstrateContext(SampleSubstrate()):
                    spec = define_wing(pitch, kind)
                    c = wing_circuit(pitch, kind)
                    board = box(
                        -spec["width_mm"] / 2,
                        -spec["height_mm"] / 2,
                        spec["width_mm"] / 2,
                        spec["height_mm"] / 2,
                    )
                    if kind == "representative21":
                        self.assertFalse(spec["size_requirement"]["fits"])
                        self.assertGreater(spec["width_mm"], 100)
                    else:
                        self.assertLessEqual(spec["width_mm"], 100)
                        self.assertLessEqual(spec["height_mm"], 100)
                    self.assertTrue(board.covers(box(*spec["connector_cable_access_mm"])))
                    pads = []
                    for component_trace, part in visit(c, Component):
                        pose = component_trace.transform * part.transform
                        for pad_trace, pad in visit(part, Pad):
                            shape = (
                                pad.shape.shape if isinstance(pad.shape, PadShape) else pad.shape
                            )
                            placed = (
                                pose * pad_trace.transform * pad.transform * shape
                            ).to_shapely()
                            placed = loads(str(placed.wkt))
                            name = str(component_trace.path)
                            self.assertTrue(board.buffer(-0.5).covers(placed), name)
                            for hole in spec["mounting_holes"]:
                                keepout = Point(hole["x_mm"], hole["y_mm"]).buffer(2.5)
                                self.assertFalse(placed.intersects(keepout), name)
                            pads.append((name, placed))
                    for i, (left, lshape) in enumerate(pads):
                        for right, rshape in pads[i + 1 :]:
                            if left != right:
                                self.assertLessEqual(
                                    lshape.intersection(rshape).area,
                                    1e-9,
                                    f"{kind}/{pitch}: {left} overlaps {right}",
                                )

    def test_piantor_source_and_relative_geometry(self):
        source = json.loads((ROOT / "wing/piantor_left21.json").read_text())
        keys = source["keys"]
        self.assertEqual(len(keys), 21)
        self.assertEqual(sum("_R" in k["id"] for k in keys), 18)
        self.assertEqual(sum("_T" in k["id"] for k in keys), 3)
        for pitch in (16.0, 17.0):
            spec = define_wing(pitch, "representative21")
            sites = {s["source_key_id"]: s for s in spec["sensor_sites"]}
            # Every pair must preserve the source relative shape, including thumbs.
            for left in keys:
                for right in keys:
                    self.assertAlmostEqual(
                        sites[left["id"]]["x_mm"] - sites[right["id"]]["x_mm"],
                        (left["x"] - right["x"]) * pitch,
                    )
                    self.assertAlmostEqual(
                        sites[left["id"]]["y_mm"] - sites[right["id"]]["y_mm"],
                        -(left["y"] - right["y"]) * pitch,
                    )
            xs, ys = zip(*spec["outline_mm"], strict=True)
            self.assertEqual(max(xs) - min(xs), spec["width_mm"])
            self.assertEqual(max(ys) - min(ys), spec["height_mm"])
            board = box(min(xs), min(ys), max(xs), max(ys))
            for site in sites.values():
                x, y = site["x_mm"], site["y_mm"]
                self.assertTrue(
                    board.covers(box(x - pitch / 2, y - pitch / 2, x + pitch / 2, y + pitch / 2))
                )

    def test_coverage_geometry_and_export_reproducibility(self):
        for kind in ("pitch9", "representative21", "load21"):
            a, b = [define_wing(p, kind) for p in (16.0, 17.0)]
            self.assertEqual(a["nets"], b["nets"])
            self.assertEqual(a["intentional_nc"], b["intentional_nc"])
            if kind != "representative21":
                self.assertEqual(a["outline_mm"], b["outline_mm"])
            self.assertEqual(
                Counter(s["mux"] for s in a["sensor_sites"]),
                {f"U_MUX_{g}": 3 if kind == "pitch9" else 7 for g in "ABC"},
            )
            for spec in (a, b):
                for group in "ABC":
                    self.assertIn(
                        f"U_MUX_{group}.9", spec["intentional_nc"]
                    )  # physical S8 = code 7
                    self.assertIn(f"U_MUX_{group}.3", spec["intentional_nc"])  # NC pin
                self.assertEqual(
                    len(spec["nets"]["GND"]), 6 + (9 if kind == "pitch9" else 21) * 2 + 3 * 2 + 4
                )
        for pitch in (16.0, 16.25, 16.75, 17.0):
            spec = define_wing(pitch, "representative21")
            self.assertEqual(len(spec["sensor_sites"]), 21)
            self.assertTrue(all(math.isfinite(s["x_mm"]) for s in spec["sensor_sites"]))
        for pitch in (15, 18, math.nan, math.inf):
            with self.assertRaises(ValueError):
                define_wing(pitch)
        export_all(ROOT / "wing/generated", check=True)
