"""Manufacturer-figure structural tests; no source-string assertions.

RP2040: printed pp. 608, 611-614; ST DS4260 Rev7 pp. 1,12;
HRO exact M-12 sheet dated 2020-12-08; Winbond RevJ pp. 5,67.
"""

from jitx.inspect import extract
from jitx.landpattern import Pad
from jitx.net import Port
from jitx.sample import SampleSubstrate
from jitx.substrate import SubstrateContext
from jitx.test import TestCase
from jitxlib.landpatterns.pads import NPTHPad, THPad

from he_piantor_42_jitx.components.connectors.hro_type_c_31_m_12 import TYPE_C_31_M_12
from he_piantor_42_jitx.components.mcu.raspberry_pi_rp2040 import RP2040
from he_piantor_42_jitx.components.memory.winbond_w25q16jvuxiq import W25Q16JVUXIQ
from he_piantor_42_jitx.components.protection.st_usblc6_2sc6 import USBLC6_2SC6


class RemainingComponentTest(TestCase):
    def check_identity_inventory(self, component, manufacturer, mpn, jlc, ports, pads):
        self.assertEqual(component.manufacturer, manufacturer)
        self.assertEqual(component.mpn, mpn)
        self.assertEqual(component.jlcpcb_part_number, jlc)
        self.assertEqual(
            component.reference_designator_prefix, "J" if manufacturer == "HRO" else "U"
        )
        self.assertTrue(component.datasheet.startswith("https://"))
        self.assertIsNone(component.value)
        self.assertEqual(len(list(extract(component, Port))), ports)
        self.assertEqual(len(list(extract(component.landpattern, Pad))), pads)

    def check_rect(self, pad, width, height, x=None, y=None):
        bounds = pad.shape.to_shapely().bounds
        for actual, expected in zip(
            bounds, [-width / 2, -height / 2, width / 2, height / 2], strict=True
        ):
            self.assertAlmostEqual(actual, expected)
        if x is not None:
            self.assertAlmostEqual(pad.transform.translation[0], x)
            self.assertAlmostEqual(pad.transform.translation[1], y)

    def test_rp2040_entire_manufacturer_pin_map(self):
        with SubstrateContext(SampleSubstrate()):
            c = RP2040()
            self.check_identity_inventory(c, "Raspberry Pi", "RP2040", "C2040", 57, 57)
            # Independent transcription from top-view manufacturer figure 170.
            physical = [
                c.IOVDD_1,
                c.GPIO0,
                c.GPIO1,
                c.GPIO2,
                c.GPIO3,
                c.GPIO4,
                c.GPIO5,
                c.GPIO6,
                c.GPIO7,
                c.IOVDD_10,
                c.GPIO8,
                c.GPIO9,
                c.GPIO10,
                c.GPIO11,
                c.GPIO12,
                c.GPIO13,
                c.GPIO14,
                c.GPIO15,
                c.TESTEN,
                c.XIN,
                c.XOUT,
                c.IOVDD_22,
                c.DVDD_23,
                c.SWCLK,
                c.SWDIO,
                c.RUN,
                c.GPIO16,
                c.GPIO17,
                c.GPIO18,
                c.GPIO19,
                c.GPIO20,
                c.GPIO21,
                c.IOVDD_33,
                c.GPIO22,
                c.GPIO23,
                c.GPIO24,
                c.GPIO25,
                c.GPIO26,
                c.GPIO27,
                c.GPIO28,
                c.GPIO29,
                c.IOVDD_42,
                c.ADC_AVDD,
                c.VREG_IN,
                c.VREG_VOUT,
                c.USB_DM,
                c.USB_DP,
                c.USB_VDD,
                c.IOVDD_49,
                c.DVDD_50,
                c.QSPI_SD3,
                c.QSPI_SCLK,
                c.QSPI_SD0,
                c.QSPI_SD2,
                c.QSPI_SD1,
                c.QSPI_CSn,
                c.GND,
            ]
            lp = c.landpattern
            pads = [*lp.left, *lp.bottom, *lp.right, *lp.top, lp.exposed]
            for port, pad in zip(physical, pads, strict=True):
                self.assertIs(c.mappings[0][port], pad)
            self.assertIs(c.mappings[0][c.GPIO26], lp.right[9])  # physical 38 ADC0
            self.assertEqual(len({id(p) for p in physical}), 57)

    def test_rp2040_reduced_ep_and_recommended_lands(self):
        with SubstrateContext(SampleSubstrate()):
            lp = RP2040().landpattern
            # Exact recommended drawing: .20 width, .40 pitch, 7.75 outer span.
            for i, pad in enumerate(lp.left):
                self.check_rect(pad, 0.875, 0.20, -3.4375, 2.6 - i * 0.4)
            for i, pad in enumerate(lp.bottom):
                self.check_rect(pad, 0.20, 1.175, -2.6 + i * 0.4, -3.2875)
            for i, pad in enumerate(lp.right):
                self.check_rect(pad, 0.875, 0.20, 3.4375, -2.6 + i * 0.4)
            for i, pad in enumerate(lp.top):
                self.check_rect(pad, 0.20, 1.175, 2.6 - i * 0.4, 3.2875)
            self.check_rect(lp.exposed, 3.20, 3.20, 0, 0)

    def test_st_exact_pin_map_and_sot_geometry(self):
        with SubstrateContext(SampleSubstrate()):
            c = USBLC6_2SC6()
            self.check_identity_inventory(c, "STMicroelectronics", "USBLC6-2SC6", "C7519", 6, 6)
            for n, port in enumerate([c.IO1_1, c.GND, c.IO2_1, c.IO2_2, c.VBUS, c.IO1_2], 1):
                self.assertIs(c.mappings[0][port], c.landpattern.p[n])
            # Pin the real generated IPC C lands and 0.95 pitch, not source parameters.
            for n in range(1, 7):
                p = c.landpattern.p[n]
                self.check_rect(
                    p,
                    0.95,
                    0.42,
                    -1.175 if n <= 3 else 1.175,
                    [0.95, 0, -0.95, -0.95, 0, 0.95][n - 1],
                )

    def test_winbond_ux_pin_map_and_exposed_metal(self):
        with SubstrateContext(SampleSubstrate()):
            c = W25Q16JVUXIQ()
            self.check_identity_inventory(c, "Winbond", "W25Q16JVUXIQ", "C2843335", 9, 9)
            for n, port in enumerate(
                [c.CS, c.QSPI_SD1, c.QSPI_SD2, c.GND, c.QSPI_SD0, c.QSPI_SCLK, c.QSPI_SD3, c.VCC], 1
            ):
                self.assertIs(c.mappings[0][port], c.landpattern.p[n])
            self.assertIs(c.mappings[0][c.EP], c.landpattern.thermal_pads[0])
            self.check_rect(c.landpattern.thermal_pads[0], 0.20, 1.60, 0, 0)
            for n in range(1, 9):
                p = c.landpattern.p[n]
                self.check_rect(
                    p,
                    0.7118033988749897,
                    0.22,
                    -1.3940983005625052 if n <= 4 else 1.3940983005625052,
                    [0.75, 0.25, -0.25, -0.75, -0.75, -0.25, 0.25, 0.75][n - 1],
                )

    def test_hro_contacts_shell_and_locators(self):
        with SubstrateContext(SampleSubstrate()):
            c = TYPE_C_31_M_12()
            self.check_identity_inventory(c, "HRO", "TYPE-C-31-M-12", "C165948", 13, 16)
            lp = c.landpattern
            ports = [
                c.A1_B12,
                c.A4_B9,
                c.B8,
                c.A5,
                c.B7,
                c.A6,
                c.A7,
                c.B6,
                c.A8,
                c.B5,
                c.A9_B4,
                c.A12_B1,
            ]
            for port, pad, (x, width) in zip(
                ports,
                lp.contacts,
                [
                    (-3.2, 0.6),
                    (-2.4, 0.6),
                    (-1.75, 0.3),
                    (-1.25, 0.3),
                    (-0.75, 0.3),
                    (-0.25, 0.3),
                    (0.25, 0.3),
                    (0.75, 0.3),
                    (1.25, 0.3),
                    (1.75, 0.3),
                    (2.4, 0.6),
                    (3.2, 0.6),
                ],
                strict=True,
            ):
                self.assertIs(c.mappings[0][port], pad)
                self.check_rect(pad, width, 1.14, x, 1.07)
            self.assertEqual(c.mappings[0][c.SHIELD], lp.shell)
            self.assertEqual(len(list(extract(lp, THPad))), 4)
            for pad, (x, y, height, hole_height) in zip(
                lp.shell,
                [
                    (-4.325, 0.5, 2.0, 1.7),
                    (4.325, 0.5, 2.0, 1.7),
                    (-4.325, -3.68, 1.7, 1.4),
                    (4.325, -3.68, 1.7, 1.4),
                ],
                strict=True,
            ):
                self.check_rect(pad, 0.9, height, x, y)
                b = pad.cutout.shape.to_shapely().bounds
                for a, e in zip(b, [-0.3, -hole_height / 2, 0.3, hole_height / 2], strict=True):
                    self.assertAlmostEqual(a, e)
                self.assertIsNone(pad.paste)
            self.assertEqual(len(list(extract(lp, NPTHPad))), 2)
            for hole, x in zip(lp.locating, [-2.89, 2.89], strict=True):
                self.assertEqual(hole.transform.translation, (x, 0))
                self.assertAlmostEqual(hole.cutout.shape.diameter, 0.60)
