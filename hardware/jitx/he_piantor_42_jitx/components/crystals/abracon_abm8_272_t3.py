"""Abracon ABM8-272-T3 12 MHz crystal.

Source: Abracon ABM8 ceramic SMD crystal datasheet, revised 2020-07-29,
page 2, outline drawing and recommended land pattern:
https://abracon.com/Resonators/abm8.pdf
"""

from jitx import PadMapping
from jitx.component import Component
from jitx.landpattern import Landpattern
from jitx.net import Port
from jitx.shapes.composites import rectangle
from jitxlib.landpatterns.pads import SMDPad
from jitxlib.symbols.box import BoxSymbol


class ABM8Landpattern(Landpattern):
    """Manufacturer-recommended ABM8 four-pad land pattern, in millimetres."""

    p1 = SMDPad(rectangle(1.30, 1.05)).at(-1.15, 0.875)
    p2 = SMDPad(rectangle(1.30, 1.05)).at(-1.15, -0.875)
    p3 = SMDPad(rectangle(1.30, 1.05)).at(1.15, -0.875)
    p4 = SMDPad(rectangle(1.30, 1.05)).at(1.15, 0.875)


class ABM8_272_T3(Component):
    """12 MHz four-pad ceramic SMD crystal, bottom-view pin ordering."""

    manufacturer = "Abracon"
    mpn = "ABM8-272-T3"
    datasheet = "https://abracon.com/Resonators/abm8.pdf"
    reference_designator_prefix = "Y"
    jlcpcb_part_number = "C20625731"

    XIN = Port()
    GND1 = Port()
    XOUT = Port()
    GND2 = Port()

    landpattern = ABM8Landpattern()
    symbol = BoxSymbol()

    def __init__(self) -> None:
        self.mappings = [
            PadMapping(
                {
                    self.XIN: self.landpattern.p1,
                    self.GND1: self.landpattern.p2,
                    self.XOUT: self.landpattern.p3,
                    self.GND2: self.landpattern.p4,
                },
            ),
        ]
