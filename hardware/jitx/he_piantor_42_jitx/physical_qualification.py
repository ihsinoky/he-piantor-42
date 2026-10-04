"""Disposable C4B geometry, NOT physical Rev.M1 or production policy.

Electrical assembly is inherited unchanged from C2. Only placement and a small
source-route experiment are added. This deliberately incomplete board must not
be fabricated. No geometry is sourced from hardware/layout or the legacy board.
"""

from jitx.board import Board
from jitx.circuit import Route
from jitx.constraints import IsCopper, IsPad, IsTrace, design_constraint
from jitx.design import Design
from jitx.feature import Soldermask
from jitx.net import PortAttachment
from jitx.shapes.composites import rectangle
from jitx.stackup import Conductor, Dielectric, Stackup
from jitx.substrate import FabricationConstraints, Substrate
from jitx.via import Via, ViaType

from .m1 import M1ElectricalCircuit


class QualificationMask(Dielectric):
    representing = Soldermask


class QualificationFR4(Dielectric):
    """Nominal qualification material only; no impedance or laminate claim."""

    dielectric_coefficient = 4.2
    loss_tangent = 0.02


class QualificationStackup(Stackup):
    """1.2 mm nominal total including modeled mask; 1.17 mm excluding mask."""

    top_mask = QualificationMask(thickness=0.015)
    top = Conductor(thickness=0.035, name="Top")
    core = QualificationFR4(thickness=1.10)
    bottom = Conductor(thickness=0.035, name="Bottom")
    bottom_mask = QualificationMask(thickness=0.015)


class QualificationFabRules(FabricationConstraints):
    """Ordinary conservative qualification defaults, not certified fab policy.

    JITX documents only the first four copper fields as engine-enforced.
    Other fields are documentary limits and require separate checking.
    """

    min_copper_width = 0.15
    min_copper_copper_space = 0.15
    min_copper_hole_space = 0.25
    min_copper_edge_space = 0.5
    min_annular_ring = 0.15
    min_drill_diameter = 0.3
    min_pitch_leaded = 0.4
    min_pitch_bga = 0.5
    max_board_width = 80.0
    max_board_height = 60.0
    min_silkscreen_width = 0.15
    min_silk_solder_mask_space = 0.15
    min_silkscreen_text_height = 1.0
    solder_mask_registration = 0.05
    min_soldermask_opening = 0.15
    min_soldermask_bridge = 0.1
    min_th_pad_expand_outer = 0.1
    min_hole_to_hole = 0.25
    min_pth_pin_solder_clearance = 0.2


class QualificationSubstrate(Substrate):
    stackup = QualificationStackup()
    constraints = QualificationFabRules()

    class ThroughVia(Via):
        type = ViaType.MechanicalDrill
        start_layer = 0
        stop_layer = 1
        diameter = 0.65
        hole_diameter = 0.3
        tented = True


class QualificationBoard(Board):
    """Project-owned 80 x 60 mm rectangle; disposable, non-authoritative."""

    shape = rectangle(80, 60)
    signal_area = rectangle(79, 59)


class M1PhysicalQualificationCircuit(M1ElectricalCircuit):
    """Reuse all C2 components/nets; no replacement wiring or component fork."""

    def __init__(self) -> None:
        super().__init__()
        # Inset the accepted connector lands from the edge for qualification.
        self.J_USB.at(-25, -24.5)
        self.U_ESD.at(-25, -18)
        self.R_CC1.at(-32, -20, rotate=90)
        self.R_CC2.at(-18, -20, rotate=90)
        self.R_USB_DP.at(-22, -12, rotate=90)
        self.R_USB_DM.at(-25, -12, rotate=90)
        # MCU, QSPI, crystal and decoupling island; deliberately generous space.
        self.U_MCU.at(-14, 0)
        self.U_FLASH.at(-3, 6, rotate=90)
        self.Y1.at(-25, 6)
        self.R_QSPI_SS.at(-3, 11)
        self.C_FLASH.at(2, 6, rotate=90)
        self.R_XOUT.at(-25, 10)
        self.C_XIN.at(-29, 6, rotate=90)
        self.C_XOUT.at(-21, 6, rotate=90)
        self.C_MCU_HF1.at(-20, -5)
        self.C_MCU_HF2.at(-17, -5)
        self.C_MCU_HF3.at(-14, -5)
        self.C_MCU_HF4.at(-11, -5)
        self.C_MCU_HF5.at(-8, -5)
        self.C_MCU_HF6.at(-20, 4)
        self.C_MCU_HF7.at(-17, 5)
        self.C_MCU_HF8.at(-14, 5)
        self.C_MCU_HF9.at(-11, 5)
        self.C_VREG_IN.at(-8, 4)
        self.C_VREG_OUT.at(-7, 0, rotate=90)
        self.C_MCU_BULK.at(-20, 0, rotate=90)
        self.SW_BOOT.at(-3, 16)
        self.SW_RUN.at(-14, 16)
        self.D_STATUS.at(-24, 16)
        self.R_STATUS_LED.at(-28, 16)
        # Regulator / load switch island.
        self.U_LDO.at(5, -18)
        self.U_LOAD.at(15, -18)
        self.C_LDO_IN.at(1, -22)
        self.C_LDO_OUT.at(9, -22)
        self.C_LOAD_IN.at(12, -22)
        self.C_LOAD_OUT.at(18, -22)
        self.D_POWER.at(5, -12)
        self.R_POWER_LED.at(9, -12)
        # Four Hall channels and mux, with room to inspect route experiments.
        self.U_MUX.at(16, 0)
        self.C_MUX.at(21, -5)
        self.R_ADC_TOP.at(6, 0, rotate=90)
        self.R_ADC_BOTTOM.at(6, 4, rotate=90)
        self.C_ADC.at(6, 8, rotate=90)
        self.U_H0.at(28, -12)
        self.U_H1.at(28, -4)
        self.U_H2.at(28, 4)
        self.U_H3.at(28, 12)
        self.C_HALL0.at(24, -12, rotate=90)
        self.C_HALL1.at(24, -4, rotate=90)
        self.C_HALL2.at(24, 4, rotate=90)
        self.C_HALL3.at(24, 12, rotate=90)
        # Accessible qualification probe locations, all on top.
        self.TP_VBUS.at(0, -26)
        self.TP_3V3.at(7, -26)
        self.TP_HALL_5V.at(16, -26)
        self.TP_GND.at(24, -26)
        self.TP_H0_RAW.at(35, -12)
        self.TP_H1_RAW.at(35, -4)
        self.TP_H2_RAW.at(35, 4)
        self.TP_H3_RAW.at(35, 12)
        self.TP_MUX_D.at(10, 8)
        self.TP_ADC_SENSE.at(6, 12)
        self.TP_SWDIO.at(-16, 24)
        self.TP_SWCLK.at(-12, 24)
        self.TP_RUN.at(-8, 24)
        self.TP_MUX_S5.at(10, 20)
        self.TP_MUX_S6.at(14, 20)
        self.TP_MUX_S7.at(18, 20)
        self.TP_MUX_S8.at(22, 20)
        # Explicit two-layer experiment, NOT a complete-board auto-route claim.
        self.h0_vias = [
            QualificationSubstrate.ThroughVia().at(31, -12),
            QualificationSubstrate.ThroughVia().at(33, -12),
        ]
        self.h0_attachments = [PortAttachment(self.U_H0.OUT, via) for via in self.h0_vias]
        self.routes = [
            Route(self.U_H0.OUT, self.h0_vias[0], 0),
            Route(self.h0_vias[0], self.h0_vias[1], 1),
            Route(self.h0_vias[1], self.TP_H0_RAW.pin1, 0),
            Route(self.U_H1.OUT, self.TP_H1_RAW.pin1, 0),
            Route(self.U_H2.OUT, self.TP_H2_RAW.pin1, 0),
            Route(self.U_H3.OUT, self.TP_H3_RAW.pin1, 0),
        ]


class M1FourKeyPhysicalQualification(Design):
    """Backend qualification fixture only; never an orderable product board."""

    board = QualificationBoard()
    substrate = QualificationSubstrate()
    circuit = M1PhysicalQualificationCircuit()
    rules = [
        design_constraint(IsTrace).trace_width(0.2),
        design_constraint(IsCopper, IsCopper).clearance(0.2),
        design_constraint(IsPad).thermal_relief(0.25, 0.25, 4),
    ]
