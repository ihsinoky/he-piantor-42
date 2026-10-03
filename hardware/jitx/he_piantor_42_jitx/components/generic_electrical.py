"""Non-MPN generic C2 models; physical choices are non-authoritative.

Values and LED colors come from the frozen M1 source. SMT(0402/0603) is
standard-library build scaffolding, including the two-terminal button. The
button represents a normally-open contact, not a resistor or a permanent link.
No manufacturer/supplier identity or geometry parity is claimed.
"""

from jitx.component import Component
from jitx.landpattern import Landpattern
from jitx.net import Port
from jitx.shapes.primitive import Circle
from jitx.units import F, PlainQuantity
from jitxlib.landpatterns.pads import SMDPad
from jitxlib.landpatterns.twopin.smt import SMT
from jitxlib.symbols.box import BoxSymbol


class Capacitor(Component):
    p1 = Port()
    p2 = Port()
    landpattern = SMT("0402")
    symbol = BoxSymbol()
    reference_designator_prefix = "C"
    capacitance: PlainQuantity

    def __init__(self, *, capacitance: float) -> None:
        if capacitance <= 0:
            raise ValueError("capacitance must be positive")
        self.capacitance = F.from_(capacitance, strict=False)
        self.value = self.capacitance


class LED(Component):
    anode = Port()
    cathode = Port()
    landpattern = SMT("0603")
    symbol = BoxSymbol()
    reference_designator_prefix = "D"

    def __init__(self, *, color: str) -> None:
        self.color = color
        self.value = f"{color} LED"


class PushButton(Component):
    pin1 = Port()
    pin2 = Port()
    landpattern = SMT("0603")
    symbol = BoxSymbol()
    reference_designator_prefix = "SW"
    value = "normally-open pushbutton"


class TestPointLandpattern(Landpattern):
    # Project-owned golden TP pad diameter; no placement or geometry comparison.
    pad = SMDPad(Circle(diameter=1.2)).at(0, 0)


class TestPoint(Component):
    pin1 = Port()
    landpattern = TestPointLandpattern()
    symbol = BoxSymbol()
    reference_designator_prefix = "TP"
