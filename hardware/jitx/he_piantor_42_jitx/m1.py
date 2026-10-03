"""Frozen M1 electrical assembly. No authoritative physical layout is defined."""

from jitx.circuit import Circuit
from jitx.net import Net
from jitx.sample import SampleDesign

from .components.connectors.hro_type_c_31_m_12 import TYPE_C_31_M_12
from .components.crystals.abracon_abm8_272_t3 import ABM8_272_T3
from .components.generic_electrical import LED, Capacitor, PushButton, TestPoint
from .components.mcu.raspberry_pi_rp2040 import RP2040
from .components.memory.winbond_w25q16jvuxiq import W25Q16JVUXIQ
from .components.power.diodes_ap2112k_3_3trg1 import AP2112K_3_3TRG1
from .components.power.texas_instruments_tps22919dckr import TPS22919DCKR
from .components.protection.st_usblc6_2sc6 import USBLC6_2SC6
from .components.resistor import Resistor
from .components.sensors.texas_instruments_drv5055a3qdbzr import DRV5055A3QDBZR
from .components.switches.texas_instruments_tmux1208pwr import TMUX1208PWR


class M1ElectricalCircuit(Circuit):
    J_USB = TYPE_C_31_M_12()
    U_ESD = USBLC6_2SC6()
    U_MCU = RP2040()
    U_FLASH = W25Q16JVUXIQ()
    Y1 = ABM8_272_T3()
    U_LDO = AP2112K_3_3TRG1()
    U_LOAD = TPS22919DCKR()
    U_MUX = TMUX1208PWR()
    U_H0 = DRV5055A3QDBZR()
    U_H1 = DRV5055A3QDBZR()
    U_H2 = DRV5055A3QDBZR()
    U_H3 = DRV5055A3QDBZR()
    R_CC1 = Resistor(resistance=5100)
    R_CC2 = Resistor(resistance=5100)
    R_USB_DP = Resistor(resistance=27)
    R_USB_DM = Resistor(resistance=27)
    R_QSPI_SS = Resistor(resistance=1000)
    R_ADC_TOP = Resistor(resistance=6800)
    R_ADC_BOTTOM = Resistor(resistance=10000)
    R_XOUT = Resistor(resistance=1000)
    R_POWER_LED = Resistor(resistance=1500)
    R_STATUS_LED = Resistor(resistance=1500)
    C_ADC = Capacitor(capacitance=1e-09)
    C_XIN = Capacitor(capacitance=1.5e-11)
    C_XOUT = Capacitor(capacitance=1.5e-11)
    C_MCU_HF1 = Capacitor(capacitance=1e-07)
    C_MCU_HF2 = Capacitor(capacitance=1e-07)
    C_MCU_HF3 = Capacitor(capacitance=1e-07)
    C_MCU_HF4 = Capacitor(capacitance=1e-07)
    C_MCU_HF5 = Capacitor(capacitance=1e-07)
    C_MCU_HF6 = Capacitor(capacitance=1e-07)
    C_MCU_HF7 = Capacitor(capacitance=1e-07)
    C_MCU_HF8 = Capacitor(capacitance=1e-07)
    C_MCU_HF9 = Capacitor(capacitance=1e-07)
    C_VREG_IN = Capacitor(capacitance=1e-06)
    C_VREG_OUT = Capacitor(capacitance=1e-06)
    C_MCU_BULK = Capacitor(capacitance=1e-05)
    C_LDO_IN = Capacitor(capacitance=1e-06)
    C_LDO_OUT = Capacitor(capacitance=1e-06)
    C_LOAD_IN = Capacitor(capacitance=1e-06)
    C_LOAD_OUT = Capacitor(capacitance=1e-06)
    C_FLASH = Capacitor(capacitance=1e-07)
    C_MUX = Capacitor(capacitance=1e-07)
    C_HALL0 = Capacitor(capacitance=1e-07)
    C_HALL1 = Capacitor(capacitance=1e-07)
    C_HALL2 = Capacitor(capacitance=1e-07)
    C_HALL3 = Capacitor(capacitance=1e-07)
    D_POWER = LED(color="green")
    D_STATUS = LED(color="amber")
    SW_BOOT = PushButton()
    SW_RUN = PushButton()
    TP_VBUS = TestPoint()
    TP_3V3 = TestPoint()
    TP_HALL_5V = TestPoint()
    TP_H0_RAW = TestPoint()
    TP_H1_RAW = TestPoint()
    TP_H2_RAW = TestPoint()
    TP_H3_RAW = TestPoint()
    TP_MUX_D = TestPoint()
    TP_ADC_SENSE = TestPoint()
    TP_GND = TestPoint()
    TP_SWDIO = TestPoint()
    TP_SWCLK = TestPoint()
    TP_RUN = TestPoint()
    TP_MUX_S5 = TestPoint()
    TP_MUX_S6 = TestPoint()
    TP_MUX_S7 = TestPoint()
    TP_MUX_S8 = TestPoint()

    def __init__(self) -> None:
        self.VBUS = Net(
            [
                self.J_USB.A4_B9,
                self.J_USB.A9_B4,
                self.U_ESD.VBUS,
                self.U_LDO.VIN,
                self.U_LDO.EN,
                self.U_LOAD.IN,
                self.C_LDO_IN.p1,
                self.C_LOAD_IN.p1,
                self.TP_VBUS.pin1,
            ],
            name="VBUS",
        )
        self.V3V3 = Net(
            [
                self.U_MCU.IOVDD_1,
                self.U_MCU.IOVDD_10,
                self.U_MCU.IOVDD_22,
                self.U_MCU.IOVDD_33,
                self.U_MCU.IOVDD_42,
                self.U_MCU.IOVDD_49,
                self.U_MCU.USB_VDD,
                self.U_MCU.ADC_AVDD,
                self.U_MCU.VREG_IN,
                self.U_FLASH.VCC,
                self.U_LDO.VOUT,
                self.C_MCU_HF1.p1,
                self.C_MCU_HF2.p1,
                self.C_MCU_HF3.p1,
                self.C_MCU_HF4.p1,
                self.C_MCU_HF5.p1,
                self.C_MCU_HF6.p1,
                self.C_MCU_HF7.p1,
                self.C_MCU_HF8.p1,
                self.C_VREG_IN.p1,
                self.C_MCU_BULK.p1,
                self.C_LDO_OUT.p1,
                self.C_FLASH.p1,
                self.D_POWER.anode,
                self.TP_3V3.pin1,
            ],
            name="V3V3",
        )
        self.V1V1 = Net(
            [
                self.U_MCU.DVDD_23,
                self.U_MCU.DVDD_50,
                self.U_MCU.VREG_VOUT,
                self.C_MCU_HF9.p1,
                self.C_VREG_OUT.p1,
            ],
            name="V1V1",
        )
        self.GND = Net(
            [
                self.J_USB.A1_B12,
                self.J_USB.A12_B1,
                self.U_ESD.GND,
                self.U_MCU.TESTEN,
                self.U_MCU.GND,
                self.U_FLASH.GND,
                self.Y1.GND1,
                self.Y1.GND2,
                self.U_LDO.GND,
                self.U_LOAD.GND,
                self.U_MUX.GND,
                self.U_H0.GND,
                self.U_H1.GND,
                self.U_H2.GND,
                self.U_H3.GND,
                self.R_CC1.p2,
                self.R_CC2.p2,
                self.R_ADC_BOTTOM.p2,
                self.R_POWER_LED.p2,
                self.R_STATUS_LED.p2,
                self.C_ADC.p2,
                self.C_XIN.p2,
                self.C_XOUT.p2,
                self.C_MCU_HF1.p2,
                self.C_MCU_HF2.p2,
                self.C_MCU_HF3.p2,
                self.C_MCU_HF4.p2,
                self.C_MCU_HF5.p2,
                self.C_MCU_HF6.p2,
                self.C_MCU_HF7.p2,
                self.C_MCU_HF8.p2,
                self.C_MCU_HF9.p2,
                self.C_VREG_IN.p2,
                self.C_VREG_OUT.p2,
                self.C_MCU_BULK.p2,
                self.C_LDO_IN.p2,
                self.C_LDO_OUT.p2,
                self.C_LOAD_IN.p2,
                self.C_LOAD_OUT.p2,
                self.C_FLASH.p2,
                self.C_MUX.p2,
                self.C_HALL0.p2,
                self.C_HALL1.p2,
                self.C_HALL2.p2,
                self.C_HALL3.p2,
                self.SW_BOOT.pin2,
                self.SW_RUN.pin2,
                self.TP_GND.pin1,
            ],
            name="GND",
        )
        self.USB_SHIELD = Net([self.J_USB.SHIELD], name="USB_SHIELD")
        self.HALL_5V = Net(
            [
                self.U_LOAD.OUT,
                self.U_MUX.VDD,
                self.U_H0.VCC,
                self.U_H1.VCC,
                self.U_H2.VCC,
                self.U_H3.VCC,
                self.C_LOAD_OUT.p1,
                self.C_MUX.p1,
                self.C_HALL0.p1,
                self.C_HALL1.p1,
                self.C_HALL2.p1,
                self.C_HALL3.p1,
                self.TP_HALL_5V.pin1,
            ],
            name="HALL_5V",
        )
        self.USB_DP_CONN = Net([self.J_USB.A6, self.J_USB.B6, self.U_ESD.IO1_1], name="USB_DP_CONN")
        self.USB_DM_CONN = Net([self.J_USB.A7, self.J_USB.B7, self.U_ESD.IO2_1], name="USB_DM_CONN")
        self.USB_DP_ESD = Net([self.U_ESD.IO1_2, self.R_USB_DP.p1], name="USB_DP_ESD")
        self.USB_DM_ESD = Net([self.U_ESD.IO2_2, self.R_USB_DM.p1], name="USB_DM_ESD")
        self.USB_DP = Net([self.U_MCU.USB_DP, self.R_USB_DP.p2], name="USB_DP")
        self.USB_DM = Net([self.U_MCU.USB_DM, self.R_USB_DM.p2], name="USB_DM")
        self.H0_RAW = Net([self.U_MUX.S1, self.U_H0.OUT, self.TP_H0_RAW.pin1], name="H0_RAW")
        self.H1_RAW = Net([self.U_MUX.S2, self.U_H1.OUT, self.TP_H1_RAW.pin1], name="H1_RAW")
        self.H2_RAW = Net([self.U_MUX.S3, self.U_H2.OUT, self.TP_H2_RAW.pin1], name="H2_RAW")
        self.H3_RAW = Net([self.U_MUX.S4, self.U_H3.OUT, self.TP_H3_RAW.pin1], name="H3_RAW")
        self.MUX_D = Net([self.U_MUX.D, self.R_ADC_TOP.p1, self.TP_MUX_D.pin1], name="MUX_D")
        self.ADC_SENSE = Net(
            [
                self.U_MCU.GPIO26,
                self.R_ADC_TOP.p2,
                self.R_ADC_BOTTOM.p1,
                self.C_ADC.p1,
                self.TP_ADC_SENSE.pin1,
            ],
            name="ADC_SENSE",
        )
        self.HALL_PWR_EN = Net([self.U_MCU.GPIO7, self.U_LOAD.ON], name="HALL_PWR_EN")
        self.MUX_A0 = Net([self.U_MCU.GPIO2, self.U_MUX.A0], name="MUX_A0")
        self.MUX_A1 = Net([self.U_MCU.GPIO3, self.U_MUX.A1], name="MUX_A1")
        self.MUX_A2 = Net([self.U_MCU.GPIO4, self.U_MUX.A2], name="MUX_A2")
        self.MUX_EN0 = Net([self.U_MCU.GPIO5, self.U_MUX.EN], name="MUX_EN0")
        self.STATUS_LED = Net([self.U_MCU.GPIO11, self.D_STATUS.anode], name="STATUS_LED")
        self.RUN = Net([self.U_MCU.RUN, self.SW_RUN.pin1, self.TP_RUN.pin1], name="RUN")
        self.SWDIO = Net([self.U_MCU.SWDIO, self.TP_SWDIO.pin1], name="SWDIO")
        self.SWCLK = Net([self.U_MCU.SWCLK, self.TP_SWCLK.pin1], name="SWCLK")
        self.QSPI_SD0 = Net([self.U_MCU.QSPI_SD0, self.U_FLASH.QSPI_SD0], name="QSPI_SD0")
        self.QSPI_SD1 = Net([self.U_MCU.QSPI_SD1, self.U_FLASH.QSPI_SD1], name="QSPI_SD1")
        self.QSPI_SD2 = Net([self.U_MCU.QSPI_SD2, self.U_FLASH.QSPI_SD2], name="QSPI_SD2")
        self.QSPI_SD3 = Net([self.U_MCU.QSPI_SD3, self.U_FLASH.QSPI_SD3], name="QSPI_SD3")
        self.QSPI_SCLK = Net([self.U_MCU.QSPI_SCLK, self.U_FLASH.QSPI_SCLK], name="QSPI_SCLK")
        self.QSPI_SS_MCU = Net([self.U_MCU.QSPI_CSn, self.R_QSPI_SS.p1], name="QSPI_SS_MCU")
        self.QSPI_SS_FLASH = Net(
            [self.U_FLASH.CS, self.R_QSPI_SS.p2, self.SW_BOOT.pin1], name="QSPI_SS_FLASH"
        )
        self.XIN = Net([self.U_MCU.XIN, self.Y1.XIN, self.C_XIN.p1], name="XIN")
        self.XOUT_XTAL = Net([self.Y1.XOUT, self.R_XOUT.p1, self.C_XOUT.p1], name="XOUT_XTAL")
        self.XOUT = Net([self.U_MCU.XOUT, self.R_XOUT.p2], name="XOUT")
        self.CC1 = Net([], name="CC1")
        self.CC2 = Net([], name="CC2")
        self.MUX_S5 = Net([self.U_MUX.S5, self.TP_MUX_S5.pin1], name="MUX_S5")
        self.MUX_S6 = Net([self.U_MUX.S6, self.TP_MUX_S6.pin1], name="MUX_S6")
        self.MUX_S7 = Net([self.U_MUX.S7, self.TP_MUX_S7.pin1], name="MUX_S7")
        self.MUX_S8 = Net([self.U_MUX.S8, self.TP_MUX_S8.pin1], name="MUX_S8")
        # Direct links intentionally retain unnamed connectivity, as in the golden.
        self.direct_links = [
            self.J_USB.A5 + self.R_CC1.p1,
            self.J_USB.B5 + self.R_CC2.p1,
            self.D_POWER.cathode + self.R_POWER_LED.p1,
            self.D_STATUS.cathode + self.R_STATUS_LED.p1,
        ]
        # Intentional NCs and unused physical GPIOs receive no connection.


class M1FourKeyElectrical(SampleDesign):
    """Electrical challenger; sample board/substrate are non-authoritative scaffolding."""

    circuit = M1ElectricalCircuit()
