"""Structural checks for the Abracon ABM8-272-T3 model."""

from jitx.sample import SampleSubstrate
from jitx.substrate import SubstrateContext
from jitx.test import TestCase

from he_piantor_42_jitx.components.crystals.abracon_abm8_272_t3 import ABM8_272_T3


class ABM8Test(TestCase):
    def test_manufacturer_landpattern_and_bottom_view_mapping(self) -> None:
        with SubstrateContext(SampleSubstrate()):
            component = ABM8_272_T3()
            pads = [
                component.landpattern.p1,
                component.landpattern.p2,
                component.landpattern.p3,
                component.landpattern.p4,
            ]
            mapping = component.mappings[0]

            self.assertEqual(component.mpn, "ABM8-272-T3")
            self.assertEqual(component.jlcpcb_part_number, "C20625731")
            self.assertIsNone(component.value)
            self.assertEqual(len(pads), 4)
            self.assertIs(mapping[component.XIN], pads[0])
            self.assertIs(mapping[component.GND1], pads[1])
            self.assertIs(mapping[component.XOUT], pads[2])
            self.assertIs(mapping[component.GND2], pads[3])

            self.assertEqual(pads[0].shape.to_shapely().bounds, (-0.65, -0.525, 0.65, 0.525))
            self.assertEqual(pads[0].transform.translation, (-1.15, 0.875))
            self.assertEqual(pads[2].transform.translation, (1.15, -0.875))
