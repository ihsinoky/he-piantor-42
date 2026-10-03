"""Winbond W25Q16JVUXIQ, W25Q16JV Revision J, May 28 2026.
Official index: https://www.winbond.com/hq/support/documentation/levelOne.jsp?__locale=en&DocNo=DA00-W25Q16JV.1
Pin map printed p. 5; UX package p. 67; ordering pp. 72-73.
https://www.winbond.com/resource-files/W25Q16JV%20SPI%20RevJ%2005202026%20Plus.pdf
UX is USON 2x3x0.6 mm, eight signals plus narrow exposed metal (D1 x E1).
EP remains a separate physical port; this model assigns no electrical net to it.
Manufacturer gives package dimensions, no PCB land pattern; SON density C
provides IPC lands. Q suffix fixes QE=1; supply is 2.7-3.6 V, industrial -40..85 C.
"""

from jitx import PadMapping
from jitx.component import Component
from jitx.net import Port
from jitx.shapes.composites import rectangle
from jitx.toleranced import Toleranced as T
from jitxlib.landpatterns.generators.son import SON, SONLead
from jitxlib.landpatterns.ipc import DensityLevel
from jitxlib.landpatterns.leads import LeadProfile
from jitxlib.landpatterns.package import RectanglePackage
from jitxlib.symbols.box import BoxSymbol


class W25Q16JVUXIQ(Component):
    """Exact UX device, complete physical inventory including unassigned EP."""

    manufacturer = "Winbond"
    mpn = "W25Q16JVUXIQ"
    datasheet = "https://www.winbond.com/resource-files/W25Q16JV%20SPI%20RevJ%2005202026%20Plus.pdf"
    reference_designator_prefix = "U"
    jlcpcb_part_number = "C2843335"
    CS = Port()
    QSPI_SD1 = Port()
    QSPI_SD2 = Port()
    GND = Port()
    QSPI_SD0 = Port()
    QSPI_SCLK = Port()
    QSPI_SD3 = Port()
    VCC = Port()
    EP = Port()
    landpattern = (
        SON(num_leads=8)
        .density_level(DensityLevel.C)
        .package_body(
            RectanglePackage(
                width=T.min_max(2.9, 3.1), length=T.min_max(1.9, 2.1), height=T.min_max(0.5, 0.6)
            )
        )
        .lead_profile(
            LeadProfile(
                span=T.min_max(2.9, 3.1),
                pitch=0.5,
                type=SONLead(length=T.min_max(0.4, 0.5), width=T.min_max(0.2, 0.3)),
            )
        )
        .thermal_pad(shape=rectangle(0.20, 1.60))
    )
    symbol = BoxSymbol()

    def physical_ports(self) -> list[Port]:
        return [
            self.CS,
            self.QSPI_SD1,
            self.QSPI_SD2,
            self.GND,
            self.QSPI_SD0,
            self.QSPI_SCLK,
            self.QSPI_SD3,
            self.VCC,
            self.EP,
        ]

    def __init__(self) -> None:
        self.mappings = [
            PadMapping(
                {
                    **{
                        port: self.landpattern.p[i]
                        for i, port in enumerate(self.physical_ports()[:8], 1)
                    },
                    self.EP: self.landpattern.thermal_pads[0],
                }
            )
        ]
