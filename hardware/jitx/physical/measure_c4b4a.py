"""Read actual public source instances; analytically measure rectangle/circle gaps."""

import json
import math
import unittest

from jitx.inspect import visit
from jitx.landpattern import Pad, PadShape
from jitx.net import Port
from jitx.stackup import Material
from jitx.substrate import SubstrateContext
from jitx.test import TestCase

from he_piantor_42_jitx.physical_qualification import QualificationSubstrate
from he_piantor_42_jitx.usb_dfm_coupon import CouponCircuit
from physical.reproduce_c4b4a import EVIDENCE, PROJECT, write


def gap(bounds, center, radius):
    x, y = center
    return (
        math.hypot(max(bounds[0] - x, 0, x - bounds[2]), max(bounds[1] - y, 0, y - bounds[3]))
        - radius
    )


class Measure(TestCase):
    def test_source(self):
        accepted = json.loads(
            (PROJECT / "physical/c4b3-evidence/independent-source-measurements.json").read_text()
        )
        with SubstrateContext(QualificationSubstrate()):
            circuit = CouponCircuit()
            connector = circuit.J_USB
            self.assertEqual(connector.transform.translation, (0, -5))
            self.assertEqual(connector.transform.rotation, 0)
            holes = [
                {
                    "center_mm": list(h.transform.translation),
                    "diameter_mm": 2 * h.cutout.shape.radius,
                }
                for h in connector.landpattern.locating
            ]
            ports = {id(p): str(t.path) for t, p in visit(connector, Port)}
            relevant = (connector.A1_B12, connector.A12_B1, connector.A4_B9, connector.A9_B4)
            measurements, contacts = [], []
            for port, pad in zip(
                connector.contact_ports(), connector.landpattern.contacts, strict=True
            ):
                shape = pad.shape.shape if isinstance(pad.shape, PadShape) else pad.shape
                g = (pad.transform * shape).to_shapely()
                bounds = list(g.bounds)
                self.assertAlmostEqual(g.area, (bounds[2] - bounds[0]) * (bounds[3] - bounds[1]))
                row = {"endpoint": ports[id(port)], "bounds_mm": bounds}
                contacts.append(row)
                if port in relevant:
                    value = min(gap(bounds, h["center_mm"], h["diameter_mm"] / 2) for h in holes)
                    historical = next(
                        r["analytic_gap_mm"]
                        for r in accepted["usb_clearances"]
                        if r["endpoint"] == row["endpoint"]
                    )
                    self.assertLess(abs(value - historical), 0.000001)
                    measurements.append(
                        {**row, "analytic_gap_mm": value, "accepted_c4b3_gap_mm": historical}
                    )
            self.assertEqual(len(measurements), 4)
            pads = []
            for trace, pad in visit(connector, Pad):
                shape = pad.shape.shape if isinstance(pad.shape, PadShape) else pad.shape
                pads.append(
                    {
                        "path": str(trace.path),
                        "wkt_mm": (trace.transform * pad.transform * shape).to_shapely().wkt,
                    }
                )
            layers = [
                {"path": str(t.path), "thickness_mm": m.thickness}
                for t, m in visit(QualificationSubstrate().stackup, Material)
            ]
            self.assertAlmostEqual(math.fsum(r["thickness_mm"] for r in layers), 1.2)
            write(
                "source-measurements.json",
                {
                    "method": "Public TestCase/visit; exact axis-aligned rectangle distance to analytic NPTH circle edge; no circle tessellation",
                    "usb_clearances": measurements,
                    "all_contact_rectangles": contacts,
                    "all_copper_pads": pads,
                    "npth": holes,
                    "placement_mm": list(connector.transform.translation),
                    "rotation_deg": 0,
                    "board_mm": [40, 25],
                    "layers": layers,
                    "source_change_guard_mm": 0.000001,
                    "observer_tolerance_mm": 0.001,
                    "geometry_changed": False,
                },
            )


if __name__ == "__main__":
    EVIDENCE.mkdir(exist_ok=True)
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(Measure)
    )
    raise SystemExit(0 if result.wasSuccessful() else 1)
