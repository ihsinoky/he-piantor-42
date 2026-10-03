"""HRO TYPE-C-31-M-12 drawing dated 2020-12-08, sheet 4 in official family PDF.
Manufacturer page: https://en.krhro.com/Product-Details/726.html
Drawing resolved from that page's PDF Download button:
https://omo-oss-file110.thefastfile.com/portal-saas/pg2026081913505947704/cms/file/type-c-31-m-12%2612a%2612b%2612c%281%29.pdf
Use only the exact M-12 sheet, not M-12A/B/C. Recommended PCB layout,
component side, tolerance +/- .05 mm. Origin at center between locating holes.
Body 8.94 x 7.35 mm; 5 A / 20 V. PCB edge y=-4.15 (1.64-5.79). Four paired power/ground terminations
share lands; eight individual signal lands; four plated shell stakes; two NPTH.
A1_B12/A12_B1 are GND; A4_B9/A9_B4 are VBUS. A5/B5 are CC1/CC2.
A6/B6 are D+, A7/B7 are D-, A8/B8 are SBU1/SBU2.
Frozen parity uses .65 mm NPTH; this manufacturer sheet specifies .60 mm.
That discrepancy is recorded for PMO; the frozen files are not altered.
"""

from jitx import PadMapping
from jitx.component import Component
from jitx.landpattern import Landpattern
from jitx.net import Port
from jitx.shapes.composites import capsule, rectangle
from jitx.shapes.primitive import Circle
from jitxlib.landpatterns.pads import NPTHPad, SMDPad, THPad
from jitxlib.symbols.box import BoxSymbol


class TYPEC31M12Landpattern(Landpattern):
    """Manufacturer recommended component-side copper and drill geometry.

    Contact height = 1.64-.50, center = (1.64+.50)/2 above locator datum.
    Rear stakes are .50-4.18 below that datum; centers span 8.65 mm.
    All dimensions in mm from the exact M-12 recommended PCB drawing.
    """

    contacts = [
        SMDPad(rectangle(width, 1.14)).at(x, 1.07)
        for x, width in [
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
        ]
    ]
    shell = [
        THPad(capsule(0.9, 2.0), capsule(0.6, 1.7)).at(-4.325, 0.5),
        THPad(capsule(0.9, 2.0), capsule(0.6, 1.7)).at(4.325, 0.5),
        THPad(capsule(0.9, 1.7), capsule(0.6, 1.4)).at(-4.325, -3.68),
        THPad(capsule(0.9, 1.7), capsule(0.6, 1.4)).at(4.325, -3.68),
    ]
    locating = [NPTHPad(Circle(diameter=0.6)).at(x, 0) for x in [-2.89, 2.89]]


class TYPE_C_31_M_12(Component):
    """Twelve contact lands plus a semantic SHIELD port mapping all four stakes."""

    manufacturer = "HRO"
    mpn = "TYPE-C-31-M-12"
    datasheet = "https://omo-oss-file110.thefastfile.com/portal-saas/pg2026081913505947704/cms/file/type-c-31-m-12%2612a%2612b%2612c%281%29.pdf"
    reference_designator_prefix = "J"
    jlcpcb_part_number = "C165948"
    A1_B12 = Port()
    A4_B9 = Port()
    B8 = Port()
    A5 = Port()
    B7 = Port()
    A6 = Port()
    A7 = Port()
    B6 = Port()
    A8 = Port()
    B5 = Port()
    A9_B4 = Port()
    A12_B1 = Port()
    SHIELD = Port()
    landpattern = TYPEC31M12Landpattern()
    symbol = BoxSymbol()

    def contact_ports(self) -> list[Port]:
        return [
            self.A1_B12,
            self.A4_B9,
            self.B8,
            self.A5,
            self.B7,
            self.A6,
            self.A7,
            self.B6,
            self.A8,
            self.B5,
            self.A9_B4,
            self.A12_B1,
        ]

    def __init__(self) -> None:
        self.mappings = [
            PadMapping(
                {
                    **dict(zip(self.contact_ports(), self.landpattern.contacts, strict=True)),
                    self.SHIELD: self.landpattern.shell,
                }
            )
        ]
