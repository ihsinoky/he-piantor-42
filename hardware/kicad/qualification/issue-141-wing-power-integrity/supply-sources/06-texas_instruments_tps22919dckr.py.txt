"""Texas Instruments TPS22919DCKR load switch.

Sources:
    TPS22919 datasheet SLVSEN5B (May 2019), page 3 (pin functions).
    TI DCK0006A package outline 4214835/D (November 2024), pages 1-2:
    https://www.ti.com/jp/lit/pdf/mpds114f
"""

from jitx import PadMapping
from jitx.component import Component
from jitx.net import Port
from jitx.toleranced import Toleranced
from jitxlib.landpatterns.generators.sot import SOT23_6, SOTLead, SOTLeadProfile
from jitxlib.landpatterns.package import RectanglePackage
from jitxlib.symbols.box import BoxSymbol


class TPS22919DCKR(Component):
    """1.5 A load switch in the six-pin DCK (SC-70) package."""

    manufacturer = "Texas Instruments"
    mpn = "TPS22919DCKR"
    datasheet = "https://www.ti.com/lit/ds/symlink/tps22919.pdf"
    reference_designator_prefix = "U"
    jlcpcb_part_number = "C2149796"

    IN = Port()
    GND = Port()
    ON = Port()
    NC = Port()
    QOD = Port()
    OUT = Port()

    landpattern = (
        SOT23_6()
        .package_body(
            RectanglePackage(
                width=Toleranced.min_max(1.10, 1.40),
                length=Toleranced.min_max(1.85, 2.15),
                height=Toleranced.exact(1.10),
            ),
        )
        .lead_profile(
            SOTLeadProfile(
                span=Toleranced.min_max(1.80, 2.40),
                pitch=0.65,
                type=SOTLead(
                    length=Toleranced.min_max(0.26, 0.46),
                    width=Toleranced.min_max(0.15, 0.30),
                ),
            ),
        )
    )
    symbol = BoxSymbol()

    def __init__(self) -> None:
        self.mappings = [
            PadMapping(
                {
                    self.IN: self.landpattern.p[1],
                    self.GND: self.landpattern.p[2],
                    self.ON: self.landpattern.p[3],
                    self.NC: self.landpattern.p[4],
                    self.QOD: self.landpattern.p[5],
                    self.OUT: self.landpattern.p[6],
                },
            ),
        ]
