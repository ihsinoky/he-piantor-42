"""ST USBLC6-2SC6, DS4260 Rev 7 (December 2021).
Functional diagram p. 1; SOT23-6L package mechanical data p. 12.
https://www.st.com/resource/en/datasheet/usblc6-2.pdf
Two data lines and VBUS protection; no exposed pad. The requested older
usblc6-2sc6.pdf URL resolves to a Y-grade document; this is the exact part source.
"""

from jitx import PadMapping
from jitx.component import Component
from jitx.net import Port
from jitx.toleranced import Toleranced as T
from jitxlib.landpatterns.generators.sot import SOT23_6, SOTLead, SOTLeadProfile
from jitxlib.landpatterns.ipc import DensityLevel
from jitxlib.landpatterns.package import RectanglePackage
from jitxlib.symbols.box import BoxSymbol


class USBLC6_2SC6(Component):
    """All six physical SOT23-6L pins in manufacturer top-view order."""

    manufacturer = "STMicroelectronics"
    mpn = "USBLC6-2SC6"
    datasheet = "https://www.st.com/resource/en/datasheet/usblc6-2.pdf"
    reference_designator_prefix = "U"
    jlcpcb_part_number = "C7519"
    IO1_1 = Port()
    GND = Port()
    IO2_1 = Port()
    IO2_2 = Port()
    VBUS = Port()
    IO1_2 = Port()
    landpattern = (
        SOT23_6()
        .density_level(DensityLevel.C)
        .package_body(
            RectanglePackage(
                width=T.min_max(1.5, 1.75), length=T.min_max(2.8, 3.05), height=T.min_max(0.9, 1.45)
            )
        )
        .lead_profile(
            SOTLeadProfile(
                span=T.min_max(2.6, 3.0),
                pitch=0.95,
                type=SOTLead(length=T.min_max(0.3, 0.6), width=T.min_max(0.3, 0.5)),
            )
        )
    )
    symbol = BoxSymbol()

    def physical_ports(self) -> list[Port]:
        return [self.IO1_1, self.GND, self.IO2_1, self.IO2_2, self.VBUS, self.IO1_2]

    def __init__(self) -> None:
        self.mappings = [
            PadMapping(
                {port: self.landpattern.p[i] for i, port in enumerate(self.physical_ports(), 1)}
            )
        ]
