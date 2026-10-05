"""Issue #49 disposable DFM coupon: accepted geometry, never a production PCB."""

from jitx.board import Board
from jitx.circuit import Circuit
from jitx.design import Design
from jitx.feature import Silkscreen
from jitx.shapes.composites import rectangle
from jitx.shapes.primitive import Text

from .components.connectors.hro_type_c_31_m_12 import TYPE_C_31_M_12
from .physical_qualification import QualificationSubstrate


class CouponBoard(Board):
    shape = rectangle(40, 25)
    signal_area = rectangle(39, 24)


class CouponCircuit(Circuit):
    def __init__(self) -> None:
        self.J_USB = TYPE_C_31_M_12().at(0, -5)
        self.warning = [
            Silkscreen(Text("DFM TEST ONLY", 1.5).at(0, 7)),
            Silkscreen(Text("DO NOT ORDER", 1.5).at(0, 4)),
        ]


class USBDFMCoupon(Design):
    """Unpowered, unrouted, qualification only; external DFM evidence pending."""

    board = CouponBoard()
    substrate = QualificationSubstrate()
    circuit = CouponCircuit()
