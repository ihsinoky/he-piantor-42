"""Independent structural checks for the AP2112K-3.3TRG1 model."""

from jitx.inspect import extract
from jitx.net import Port
from jitx.sample import SampleSubstrate
from jitx.substrate import SubstrateContext
from jitx.test import TestCase

from he_piantor_42_jitx.components.power.diodes_ap2112k_3_3trg1 import AP2112K_3_3TRG1


class AP2112K3V3Test(TestCase):
    """Verify metadata, package inventory, and pin declaration order."""

    def test_identity_and_pin_inventory(self) -> None:
        with SubstrateContext(SampleSubstrate()):
            component = AP2112K_3_3TRG1()

            self.assertEqual(component.manufacturer, "Diodes Incorporated")
            self.assertEqual(component.mpn, "AP2112K-3.3TRG1")
            self.assertEqual(component.jlcpcb_part_number, "C51118")
            self.assertEqual(component.value, None)
            self.assertEqual(
                list(extract(component, Port)),
                [component.VIN, component.GND, component.EN, component.NC, component.VOUT],
            )

    def test_sot25_pad_count(self) -> None:
        with SubstrateContext(SampleSubstrate()):
            component = AP2112K_3_3TRG1()

            self.assertEqual(len(component.landpattern.p), 5)
            mapping = component.mappings[0]
            self.assertIs(mapping[component.VIN], component.landpattern.p[1])
            self.assertIs(mapping[component.GND], component.landpattern.p[2])
            self.assertIs(mapping[component.EN], component.landpattern.p[3])
            self.assertIs(mapping[component.NC], component.landpattern.p[4])
            self.assertIs(mapping[component.VOUT], component.landpattern.p[5])
