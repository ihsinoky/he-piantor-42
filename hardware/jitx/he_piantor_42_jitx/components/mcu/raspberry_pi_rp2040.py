"""RP2040: Raspberry Pi datasheet build 3184e62-clean, 2025-02-20.
Pinout: printed p. 611, 'RP2040 QFN-56 package pinout', and pp. 612-614.
Geometry: printed pp. 607-608, 'Recommended PCB Footprint'.
https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf
GPIO26 is ADC0 (physical pin 38); GPIO27..29 are ADC1..3.
All supplies remain separate physical ports. TESTEN must later be grounded.
The body is 7 x 7 mm, pitch 0.4 mm; the reduced GND pad is 3.20 mm.
"""

from jitx import PadMapping
from jitx.component import Component
from jitx.landpattern import Landpattern, Pad
from jitx.net import Port
from jitx.shapes.composites import rectangle
from jitxlib.landpatterns.pads import SMDPad
from jitxlib.symbols.box import BoxSymbol


class RP2040Landpattern(Landpattern):
    """Exact recommended copper; unequal side lengths preclude generic QFN.

    Figure dimensions: outer span 7.75; inner span 6.00; row extent 5.40;
    left/right length .875 and top/bottom length 1.175; width .20.
    The 6.00 inner span applies to left/right; top/bottom inner span is 5.40.
    """

    left = [SMDPad(rectangle(0.875, 0.20)).at(-3.4375, 2.6 - i * 0.4) for i in range(14)]
    bottom = [SMDPad(rectangle(0.20, 1.175)).at(-2.6 + i * 0.4, -3.2875) for i in range(14)]
    right = [SMDPad(rectangle(0.875, 0.20)).at(3.4375, -2.6 + i * 0.4) for i in range(14)]
    top = [SMDPad(rectangle(0.20, 1.175)).at(2.6 - i * 0.4, 3.2875) for i in range(14)]
    exposed = SMDPad(rectangle(3.20, 3.20)).at(0, 0)

    def physical_pads(self) -> list[Pad]:
        return [*self.left, *self.bottom, *self.right, *self.top, self.exposed]


class RP2040(Component):
    """Complete 56-pin device plus exposed GND; no M1-only aliases."""

    manufacturer = "Raspberry Pi"
    mpn = "RP2040"
    datasheet = "https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf"
    reference_designator_prefix = "U"
    jlcpcb_part_number = "C2040"
    IOVDD_1 = Port()
    GPIO0 = Port()
    GPIO1 = Port()
    GPIO2 = Port()
    GPIO3 = Port()
    GPIO4 = Port()
    GPIO5 = Port()
    GPIO6 = Port()
    GPIO7 = Port()
    IOVDD_10 = Port()
    GPIO8 = Port()
    GPIO9 = Port()
    GPIO10 = Port()
    GPIO11 = Port()
    GPIO12 = Port()
    GPIO13 = Port()
    GPIO14 = Port()
    GPIO15 = Port()
    TESTEN = Port()
    XIN = Port()
    XOUT = Port()
    IOVDD_22 = Port()
    DVDD_23 = Port()
    SWCLK = Port()
    SWDIO = Port()
    RUN = Port()
    GPIO16 = Port()
    GPIO17 = Port()
    GPIO18 = Port()
    GPIO19 = Port()
    GPIO20 = Port()
    GPIO21 = Port()
    IOVDD_33 = Port()
    GPIO22 = Port()
    GPIO23 = Port()
    GPIO24 = Port()
    GPIO25 = Port()
    GPIO26 = Port()
    GPIO27 = Port()
    GPIO28 = Port()
    GPIO29 = Port()
    IOVDD_42 = Port()
    ADC_AVDD = Port()
    VREG_IN = Port()
    VREG_VOUT = Port()
    USB_DM = Port()
    USB_DP = Port()
    USB_VDD = Port()
    IOVDD_49 = Port()
    DVDD_50 = Port()
    QSPI_SD3 = Port()
    QSPI_SCLK = Port()
    QSPI_SD0 = Port()
    QSPI_SD2 = Port()
    QSPI_SD1 = Port()
    QSPI_CSn = Port()
    GND = Port()
    landpattern = RP2040Landpattern()
    symbol = BoxSymbol()

    def physical_ports(self) -> list[Port]:
        return [
            self.IOVDD_1,
            self.GPIO0,
            self.GPIO1,
            self.GPIO2,
            self.GPIO3,
            self.GPIO4,
            self.GPIO5,
            self.GPIO6,
            self.GPIO7,
            self.IOVDD_10,
            self.GPIO8,
            self.GPIO9,
            self.GPIO10,
            self.GPIO11,
            self.GPIO12,
            self.GPIO13,
            self.GPIO14,
            self.GPIO15,
            self.TESTEN,
            self.XIN,
            self.XOUT,
            self.IOVDD_22,
            self.DVDD_23,
            self.SWCLK,
            self.SWDIO,
            self.RUN,
            self.GPIO16,
            self.GPIO17,
            self.GPIO18,
            self.GPIO19,
            self.GPIO20,
            self.GPIO21,
            self.IOVDD_33,
            self.GPIO22,
            self.GPIO23,
            self.GPIO24,
            self.GPIO25,
            self.GPIO26,
            self.GPIO27,
            self.GPIO28,
            self.GPIO29,
            self.IOVDD_42,
            self.ADC_AVDD,
            self.VREG_IN,
            self.VREG_VOUT,
            self.USB_DM,
            self.USB_DP,
            self.USB_VDD,
            self.IOVDD_49,
            self.DVDD_50,
            self.QSPI_SD3,
            self.QSPI_SCLK,
            self.QSPI_SD0,
            self.QSPI_SD2,
            self.QSPI_SD1,
            self.QSPI_CSn,
            self.GND,
        ]

    def __init__(self) -> None:
        self.mappings = [
            PadMapping(
                dict(zip(self.physical_ports(), self.landpattern.physical_pads(), strict=True))
            )
        ]
