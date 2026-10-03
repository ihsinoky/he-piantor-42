"""Texas Instruments TMUX1208PWR analog multiplexer.

Sources:
    TMUX1208/TMUX1209 datasheet SCDS389C (December 2018), page 3.
    TI PW0016A package outline 4220204/B (December 2023), pages 1-2:
    https://www.ti.com/lit/ml/mpds361a/mpds361a.pdf
"""

from jitx import PadMapping
from jitx.component import Component
from jitx.net import Port
from jitx.toleranced import Toleranced
from jitxlib.landpatterns.generators.soic import SOIC
from jitxlib.landpatterns.leads import LeadProfile, SMDLead
from jitxlib.landpatterns.leads.protrusions import BigGullWingLeads
from jitxlib.landpatterns.package import RectanglePackage
from jitxlib.symbols.box import BoxSymbol


class TMUX1208PWR(Component):
    """Eight-to-one analog multiplexer in the PW TSSOP-16 package."""

    manufacturer = "Texas Instruments"
    mpn = "TMUX1208PWR"
    datasheet = "https://www.ti.com/lit/ds/symlink/tmux1208.pdf"
    reference_designator_prefix = "U"
    jlcpcb_part_number = "C494728"

    A0 = Port()
    EN = Port()
    NC = Port()
    S1 = Port()
    S2 = Port()
    S3 = Port()
    S4 = Port()
    D = Port()
    S8 = Port()
    S7 = Port()
    S6 = Port()
    S5 = Port()
    VDD = Port()
    GND = Port()
    A2 = Port()
    A1 = Port()

    landpattern = (
        SOIC(num_leads=16)
        .package_body(
            RectanglePackage(
                width=Toleranced.min_max(4.30, 4.50),
                length=Toleranced.min_max(4.90, 5.10),
                height=Toleranced.exact(1.20),
            ),
        )
        .lead_profile(
            LeadProfile(
                span=Toleranced.min_max(6.20, 6.60),
                pitch=0.65,
                type=SMDLead(
                    length=Toleranced.min_max(0.50, 0.75),
                    width=Toleranced.min_max(0.17, 0.30),
                    lead_type=BigGullWingLeads,
                ),
            ),
        )
    )
    symbol = BoxSymbol()

    def __init__(self) -> None:
        self.mappings = [
            PadMapping(
                {
                    self.A0: self.landpattern.p[1],
                    self.EN: self.landpattern.p[2],
                    self.NC: self.landpattern.p[3],
                    self.S1: self.landpattern.p[4],
                    self.S2: self.landpattern.p[5],
                    self.S3: self.landpattern.p[6],
                    self.S4: self.landpattern.p[7],
                    self.D: self.landpattern.p[8],
                    self.S8: self.landpattern.p[9],
                    self.S7: self.landpattern.p[10],
                    self.S6: self.landpattern.p[11],
                    self.S5: self.landpattern.p[12],
                    self.VDD: self.landpattern.p[13],
                    self.GND: self.landpattern.p[14],
                    self.A2: self.landpattern.p[15],
                    self.A1: self.landpattern.p[16],
                },
            ),
        ]
