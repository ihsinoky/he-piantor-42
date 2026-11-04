"""Project-owned GH14 transcription of approved native JstGh14.tsx.

Original drawing: BM14B-GHS-TBT.pdf, KRD-32980-5 R0, 2024-03-13,
SHA256 1707350a5780a7c8a7b95e67430cc0b8ddda36ebe1a6fb04d6ab4cfc536776d1.
Mounting-surface +Y up, pin 1 right, origin signal-land midpoint.
Reinforcement lands are mechanical NC; never use them as return contacts.
"""

from jitx import PadMapping
from jitx.component import Component
from jitx.landpattern import Landpattern
from jitx.net import Port
from jitx.shapes.composites import rectangle
from jitxlib.landpatterns.pads import SMDPad
from jitxlib.symbols.box import BoxSymbol


class GH14Landpattern(Landpattern):
    contacts = [SMDPad(rectangle(0.6, 1.7)).at(8.125 - 1.25 * i, 0) for i in range(14)]
    reinforcement = [SMDPad(rectangle(1, 2.8)).at(x, -3.35) for x in (-9.975, 9.975)]


class BM14B_GHS_TBT(Component):
    manufacturer = "JST"
    mpn = "BM14B-GHS-TBT(LF)(SN)"
    reference_designator_prefix = "J"
    p = [Port() for _ in range(14)]
    MP = Port()
    landpattern = GH14Landpattern()
    symbol = BoxSymbol()

    def __init__(self):
        self.mappings = [
            PadMapping(
                {
                    **dict(zip(self.p, self.landpattern.contacts, strict=True)),
                    self.MP: self.landpattern.reinforcement,
                }
            )
        ]
