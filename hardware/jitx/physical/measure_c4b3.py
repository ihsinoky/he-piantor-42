"""Independent public-source thickness and analytic NPTH gap measurements."""

import json
import math
import unittest

from jitx.inspect import visit
from jitx.landpattern import PadShape
from jitx.net import Port
from jitx.stackup import Conductor, Material
from jitx.test import TestCase

from he_piantor_42_jitx.components.connectors.hro_type_c_31_m_12 import TYPE_C_31_M_12
from he_piantor_42_jitx.physical_qualification import QualificationStackup
from physical.requalify_c4b3 import EVIDENCE


class Measure(TestCase):
    def test_source_dimensions(self):
        layers = [
            {
                "path": str(trace.path),
                "thickness_mm": material.thickness,
                "kind": "conductor" if isinstance(material, Conductor) else "dielectric",
            }
            for trace, material in visit(QualificationStackup(), Material)
        ]
        total = math.fsum(row["thickness_mm"] for row in layers)
        self.assertAlmostEqual(total, 1.2)
        connector = TYPE_C_31_M_12()
        gaps = []
        for port, pad in zip(
            connector.contact_ports(), connector.landpattern.contacts, strict=True
        ):
            if port not in (
                connector.A1_B12,
                connector.A12_B1,
                connector.A4_B9,
                connector.A9_B4,
            ):
                continue
            shape = pad.shape.shape if isinstance(pad.shape, PadShape) else pad.shape
            bounds = (pad.transform * shape).to_shapely().bounds
            distances = []
            for hole in connector.landpattern.locating:
                x, y = hole.transform.translation
                # Exact axis-aligned rectangle to analytic circle edge: no
                # polygon approximation of the locator's circular perimeter.
                dx = max(bounds[0] - x, 0, x - bounds[2])
                dy = max(bounds[1] - y, 0, y - bounds[3])
                distances.append(math.hypot(dx, dy) - hole.cutout.shape.radius)
            endpoint = next(str(t.path) for t, p in visit(connector, Port) if p is port)
            gaps.append(
                {
                    "endpoint": endpoint,
                    "analytic_gap_mm": min(distances),
                    "nominal_margin_above_0_20_mm": min(distances) - 0.2,
                    "rectangle_bounds_mm": bounds,
                }
            )
        self.assertEqual(len(gaps), 4)
        (EVIDENCE / "independent-source-measurements.json").write_text(
            json.dumps(
                {
                    "layers": layers,
                    "total_including_masks_mm": total,
                    "total_excluding_masks_mm": math.fsum(
                        row["thickness_mm"] for row in layers if "mask" not in row["path"]
                    ),
                    "usb_clearances": gaps,
                    "method": "Public JITX TestCase/visit; rectangle-to-circle analytic edge distances",
                    "manufacturer_geometry_changed": False,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(Measure)
    )
    raise SystemExit(0 if result.wasSuccessful() else 1)
