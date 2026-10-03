"""Discoverable non-dry JITX build harnesses for M1 component models."""

import jitx
from jitx.container import inline
from jitx.sample import SampleDesign

from .components.connectors.hro_type_c_31_m_12 import TYPE_C_31_M_12
from .components.crystals.abracon_abm8_272_t3 import ABM8_272_T3
from .components.mcu.raspberry_pi_rp2040 import RP2040
from .components.memory.winbond_w25q16jvuxiq import W25Q16JVUXIQ
from .components.power.diodes_ap2112k_3_3trg1 import AP2112K_3_3TRG1
from .components.power.texas_instruments_tps22919dckr import TPS22919DCKR
from .components.protection.st_usblc6_2sc6 import USBLC6_2SC6
from .components.sensors.texas_instruments_drv5055a3qdbzr import DRV5055A3QDBZR
from .components.switches.texas_instruments_tmux1208pwr import TMUX1208PWR


class AP2112K3V3TestDesign(SampleDesign):
    """Build-only harness for the AP2112K-3.3TRG1 component model."""

    @inline
    class circuit(jitx.Circuit):
        dut = AP2112K_3_3TRG1()


class TPS22919TestDesign(SampleDesign):
    """Build-only harness for the TPS22919DCKR component model."""

    @inline
    class circuit(jitx.Circuit):
        dut = TPS22919DCKR()


class TMUX1208TestDesign(SampleDesign):
    """Build-only harness for the TMUX1208PWR component model."""

    @inline
    class circuit(jitx.Circuit):
        dut = TMUX1208PWR()


class DRV5055TestDesign(SampleDesign):
    """Build-only harness for the DRV5055A3QDBZR component model."""

    @inline
    class circuit(jitx.Circuit):
        dut = DRV5055A3QDBZR()


class ABM8TestDesign(SampleDesign):
    """Build-only harness for the ABM8-272-T3 component model."""

    @inline
    class circuit(jitx.Circuit):
        dut = ABM8_272_T3()


class RP2040TestDesign(SampleDesign):
    """Isolated component build harness."""

    @inline
    class circuit(jitx.Circuit):
        dut = RP2040()


class USBLC6TestDesign(SampleDesign):
    """Isolated component build harness."""

    @inline
    class circuit(jitx.Circuit):
        dut = USBLC6_2SC6()


class W25Q16TestDesign(SampleDesign):
    """Isolated component build harness."""

    @inline
    class circuit(jitx.Circuit):
        dut = W25Q16JVUXIQ()


class HROTestDesign(SampleDesign):
    """Isolated component build harness."""

    @inline
    class circuit(jitx.Circuit):
        dut = TYPE_C_31_M_12()
