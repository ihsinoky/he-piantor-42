"""Texas Instruments DRV5055A3QDBZR linear Hall sensor.

Sources:
    DRV5055 datasheet SBAS640C, page 3 (pin functions).
    TI DBZ0003A package outline 4214838/F (August 2024), pages 1-2:
    https://www.ti.com/cn/lit/pdf/mpds108g
"""

from jitx import PadMapping
from jitx.component import Component
from jitx.net import Port
from jitx.toleranced import Toleranced
from jitxlib.landpatterns.generators.sot import SOT23_3, SOTLead, SOTLeadProfile
from jitxlib.landpatterns.package import RectanglePackage
from jitxlib.symbols.box import BoxSymbol


class DRV5055A3QDBZR(Component):
    """Ratiometric linear Hall sensor in the DBZ SOT-23 package."""

    manufacturer = "Texas Instruments"
    mpn = "DRV5055A3QDBZR"
    datasheet = "https://www.ti.com/lit/ds/symlink/drv5055.pdf"
    reference_designator_prefix = "U"
    jlcpcb_part_number = "C266128"

    VCC = Port()
    OUT = Port()
    GND = Port()

    landpattern = (
        SOT23_3()
        .package_body(
            RectanglePackage(
                width=Toleranced.min_max(1.20, 1.40),
                length=Toleranced.min_max(2.80, 3.04),
                height=Toleranced.exact(1.12),
            ),
        )
        .lead_profile(
            SOTLeadProfile(
                span=Toleranced.min_max(2.10, 2.64),
                type=SOTLead(
                    length=Toleranced.min_max(0.30, 0.60),
                    width=Toleranced.min_max(0.20, 0.50),
                ),
            ),
        )
    )
    symbol = BoxSymbol()

    def __init__(self) -> None:
        self.mappings = [
            PadMapping(
                {
                    self.VCC: self.landpattern.p[1],
                    self.OUT: self.landpattern.p[2],
                    self.GND: self.landpattern.p[3],
                },
            ),
        ]
