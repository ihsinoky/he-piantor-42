"""Discoverable non-dry JITX build harnesses for M1 component models."""

import jitx
from jitx.container import inline
from jitx.sample import SampleDesign

from .components.power.diodes_ap2112k_3_3trg1 import AP2112K_3_3TRG1


class AP2112K3V3TestDesign(SampleDesign):
    """Build-only harness for the AP2112K-3.3TRG1 component model."""

    @inline
    class circuit(jitx.Circuit):
        dut = AP2112K_3_3TRG1()
