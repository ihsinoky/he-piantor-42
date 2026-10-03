"""Diodes Incorporated AP2112K-3.3TRG1 3.3 V LDO.

Sources:
    AP2112 datasheet DS39724 Rev. 2-2 (June 2017), pages 2 and 14:
    https://www.diodes.com/assets/Datasheets/AP2112.pdf

The SOT25 pin inventory is VIN, GND, EN, NC, and VOUT. The landpattern uses
the datasheet's SOT25 body and lead dimensions through JITX's SOT-23-5
generator. The model retains NC because it is a physical pad.
"""

from jitx import PadMapping
from jitx.component import Component
from jitx.net import Port
from jitx.toleranced import Toleranced
from jitxlib.landpatterns.generators.sot import SOT23_5, SOTLead, SOTLeadProfile
from jitxlib.landpatterns.package import RectanglePackage
from jitxlib.symbols.box import BoxSymbol


class AP2112K_3_3TRG1(Component):
    """Fixed 3.3 V, 600 mA LDO in the manufacturer's SOT25 package."""

    manufacturer = "Diodes Incorporated"
    mpn = "AP2112K-3.3TRG1"
    datasheet = "https://www.diodes.com/assets/Datasheets/AP2112.pdf"
    reference_designator_prefix = "U"
    jlcpcb_part_number = "C51118"

    VIN = Port()
    GND = Port()
    EN = Port()
    NC = Port()
    VOUT = Port()

    landpattern = (
        SOT23_5()
        .package_body(
            RectanglePackage(
                width=Toleranced.min_max(1.50, 1.70),
                length=Toleranced.min_max(2.70, 3.00),
                height=Toleranced.min_max(0.35, 0.50),
            ),
        )
        .lead_profile(
            SOTLeadProfile(
                span=Toleranced.min_max(2.90, 3.10),
                type=SOTLead(
                    length=Toleranced.min_max(0.35, 0.55),
                    width=Toleranced.min_max(0.10, 0.20),
                ),
            ),
        )
    )
    symbol = BoxSymbol()

    def __init__(self) -> None:
        self.mappings = [
            PadMapping(
                {
                    self.VIN: self.landpattern.p[1],
                    self.GND: self.landpattern.p[2],
                    self.EN: self.landpattern.p[3],
                    self.NC: self.landpattern.p[4],
                    self.VOUT: self.landpattern.p[5],
                },
            ),
        ]
