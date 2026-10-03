"""Independent structural checks for the source-grounded TI M1 component models."""

from jitx.net import Port
from jitx.sample import SampleSubstrate
from jitx.substrate import SubstrateContext
from jitx.test import TestCase

from he_piantor_42_jitx.components.power.texas_instruments_tps22919dckr import (
    TPS22919DCKR,
)
from he_piantor_42_jitx.components.sensors.texas_instruments_drv5055a3qdbzr import (
    DRV5055A3QDBZR,
)
from he_piantor_42_jitx.components.switches.texas_instruments_tmux1208pwr import (
    TMUX1208PWR,
)


class TIComponentTest(TestCase):
    """Verify manufacturer identity, physical inventory, and explicit pad maps."""

    def test_tps22919_dck_pin_mapping(self) -> None:
        with SubstrateContext(SampleSubstrate()):
            component = TPS22919DCKR()
            pins = [
                component.IN,
                component.GND,
                component.ON,
                component.NC,
                component.QOD,
                component.OUT,
            ]

            self.assertEqual(component.mpn, "TPS22919DCKR")
            self.assertEqual(component.jlcpcb_part_number, "C2149796")
            self.assertIsNone(component.value)
            self.assertTrue(all(isinstance(pin, Port) for pin in pins))
            self.assertEqual(len(component.landpattern.p), 6)
            mapping = component.mappings[0]
            for pin_number, port in enumerate(pins, start=1):
                self.assertIs(mapping[port], component.landpattern.p[pin_number])

    def test_tmux1208_pw_pin_mapping(self) -> None:
        with SubstrateContext(SampleSubstrate()):
            component = TMUX1208PWR()
            pins = [
                component.A0,
                component.EN,
                component.NC,
                component.S1,
                component.S2,
                component.S3,
                component.S4,
                component.D,
                component.S8,
                component.S7,
                component.S6,
                component.S5,
                component.VDD,
                component.GND,
                component.A2,
                component.A1,
            ]

            self.assertEqual(component.mpn, "TMUX1208PWR")
            self.assertEqual(component.jlcpcb_part_number, "C494728")
            self.assertIsNone(component.value)
            self.assertTrue(all(isinstance(pin, Port) for pin in pins))
            self.assertEqual(len(component.landpattern.p), 16)
            mapping = component.mappings[0]
            for pin_number, port in enumerate(pins, start=1):
                self.assertIs(mapping[port], component.landpattern.p[pin_number])

    def test_drv5055_dbz_pin_mapping(self) -> None:
        with SubstrateContext(SampleSubstrate()):
            component = DRV5055A3QDBZR()
            pins = [component.VCC, component.OUT, component.GND]

            self.assertEqual(component.mpn, "DRV5055A3QDBZR")
            self.assertEqual(component.jlcpcb_part_number, "C266128")
            self.assertIsNone(component.value)
            self.assertTrue(all(isinstance(pin, Port) for pin in pins))
            self.assertEqual(len(component.landpattern.p), 3)
            mapping = component.mappings[0]
            for pin_number, port in enumerate(pins, start=1):
                self.assertIs(mapping[port], component.landpattern.p[pin_number])
