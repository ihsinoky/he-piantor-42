"""Guard physical-pad coverage/NC boundaries without claiming realized copper."""

from jitx.component import Component
from jitx.inspect import visit
from jitx.landpattern import Pad, PadMapping
from jitx.net import Net, Port
from jitx.substrate import SubstrateContext
from jitx.test import TestCase

from he_piantor_42_jitx.physical_qualification import QualificationSubstrate
from he_piantor_42_jitx.routing_qualification import (
    RoutingQualificationCircuit,
    ViaRoutingQualificationCircuit,
)


class RoutingIntentTest(TestCase):
    def test_required_physical_pads_and_nc_boundary(self):
        with SubstrateContext(QualificationSubstrate()):
            circuit = RoutingQualificationCircuit()
            required_ports = {port for _, net in visit(circuit, Net) for port in net}
            pads_by_port = {}
            for _, component in visit(circuit, Component):
                mappings = list(visit(component, PadMapping))
                if mappings:
                    for _, mapping in mappings:
                        for port, pads in mapping.items():
                            pads_by_port[port] = [pads] if isinstance(pads, Pad) else list(pads)
                else:
                    for (_, port), (_, pad) in zip(
                        visit(component, Port), visit(component, Pad), strict=True
                    ):
                        pads_by_port[port] = [pad]
            required_pads = {pad for p in required_ports for pad in pads_by_port.get(p, [])}
            intended_pads = set()
            for route in circuit.routes + circuit.additional_routes:
                for endpoint in (route.source, route.destination):
                    if isinstance(endpoint, Pad):
                        intended_pads.add(endpoint)
                    else:
                        intended_pads.update(pads_by_port.get(endpoint, []))
            self.assertEqual(intended_pads, required_pads)
            # Crucial semantic-singleton/physical-four-islands case.
            shield = pads_by_port[circuit.J_USB.SHIELD]
            self.assertEqual(len(shield), 4)
            self.assertTrue(set(shield) <= intended_pads)
            all_pads = {p for _, p in visit(circuit, Pad)}
            self.assertFalse((all_pads - required_pads) & intended_pads)
            self.assertEqual(len(list(visit(circuit, Component))), 68)

    def test_multilayer_experiment_replaces_one_request(self):
        with SubstrateContext(QualificationSubstrate()):
            base = RoutingQualificationCircuit()
            via = ViaRoutingQualificationCircuit()
            self.assertEqual(len(via.additional_routes), len(base.additional_routes) - 1)
            self.assertEqual(len(via.escape_routes), 3)
            self.assertEqual([r.layer for r in via.escape_routes], [0, 1, 0])
