"""Forward C4B5 source-routing experiment; disposable and never orderable.

Use the public single-layer Route pathfinder with a nearest-pad spanning tree.
This selects endpoint intent, not copper paths: JITX must realize every request.
It is deliberately a bounded feasibility experiment, not an external router.
"""

from math import dist

from jitx.circuit import Route
from jitx.component import Component
from jitx.design import Design
from jitx.inspect import visit
from jitx.landpattern import Pad, PadMapping, PadShape
from jitx.net import Net, Port, PortAttachment

from .physical_qualification import (
    M1FourKeyPhysicalQualification,
    M1PhysicalQualificationCircuit,
    QualificationBoard,
    QualificationSubstrate,
)


class RoutingQualificationCircuit(M1PhysicalQualificationCircuit):
    """Retain C2, all manufacturer pads, all placements and the two-via test."""

    def __init__(self):
        super().__init__()
        port_pads = {}
        centers = {}
        for _, component in visit(self, Component):
            mappings = list(visit(component, PadMapping))
            if mappings:
                for _, mapping in mappings:
                    for port, pads in mapping.items():
                        port_pads[port] = [pads] if isinstance(pads, Pad) else list(pads)
            else:
                for (_, port), (_, pad) in zip(
                    visit(component, Port), visit(component, Pad), strict=True
                ):
                    port_pads[port] = [pad]
            for trace, pad in visit(component, Pad):
                shape = pad.shape.shape if isinstance(pad.shape, PadShape) else pad.shape
                geometry = (component.transform * trace.transform * pad.transform) * shape
                centers[pad] = geometry.to_shapely().centroid.coords[0]

        # Preserve already-realized Hall/probe paths, including the H0 via chain.
        existing = [
            (self.U_H0.OUT, self.TP_H0_RAW.pin1),
            (self.U_H1.OUT, self.TP_H1_RAW.pin1),
            (self.U_H2.OUT, self.TP_H2_RAW.pin1),
            (self.U_H3.OUT, self.TP_H3_RAW.pin1),
        ]
        self.additional_routes = []
        # Net iteration includes the four unnamed direct links. Empty declarations
        # and ports outside nets (intentional NCs/unused GPIOs) get no requests.
        for _, net in visit(self, Net):
            ports = list(dict.fromkeys(p for p in net if p in port_pads))
            pads = list(dict.fromkeys(pad for port in ports for pad in port_pads[port]))
            if not pads:
                continue
            groups = [{pad} for pad in pads]
            for source, destination in existing:
                if source in ports and destination in ports:
                    joined = set(port_pads[source] + port_pads[destination])
                    groups = [g for g in groups if not g & joined] + [joined]
            while len(groups) > 1:
                _, i, j, source, destination = min(
                    (
                        (dist(centers[a], centers[b]), i, j, a, b)
                        for i, left in enumerate(groups)
                        for j, right in enumerate(groups)
                        if i < j
                        for a in pads
                        if a in left
                        for b in pads
                        if b in right
                    ),
                    key=lambda candidate: candidate[:3],
                )
                self.additional_routes.append(Route(source, destination, layer=0))
                groups[i] |= groups.pop(j)


class CompleteRoutingQualification(Design):
    """C4B5 feasibility candidate, not physical Rev.M1 or production geometry."""

    board = QualificationBoard()
    substrate = QualificationSubstrate()
    circuit = RoutingQualificationCircuit()
    rules = M1FourKeyPhysicalQualification.rules


class ViaRoutingQualificationCircuit(RoutingQualificationCircuit):
    """Representative GPIO2/MUX_A0 layer escape after single-layer failure."""

    def __init__(self):
        super().__init__()
        # Replace exactly the failed MUX_A0 request, by electrical identity.
        self.additional_routes = [
            route
            for route in self.additional_routes
            if not (
                route.source in self.U_MCU.landpattern.physical_pads()
                and route.destination is self.U_MUX.landpattern.p[1]
            )
        ]
        self.escape_vias = [
            QualificationSubstrate.ThroughVia().at(-18.5, 1.4),
            QualificationSubstrate.ThroughVia().at(11.8, 2.275),
        ]
        self.escape_attachments = [
            PortAttachment(self.U_MCU.GPIO2, self.escape_vias[0]),
            PortAttachment(self.U_MUX.A0, self.escape_vias[1]),
        ]
        self.escape_routes = [
            Route(self.U_MCU.GPIO2, self.escape_vias[0], 0),
            Route(self.escape_vias[0], self.escape_vias[1], 1),
            Route(self.escape_vias[1], self.U_MUX.A0, 0),
        ]


class ViaRoutingQualification(Design):
    """Bounded multilayer experiment; completion still requires downstream DRC."""

    board = QualificationBoard()
    substrate = QualificationSubstrate()
    circuit = ViaRoutingQualificationCircuit()
    rules = M1FourKeyPhysicalQualification.rules
