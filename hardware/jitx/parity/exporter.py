"""Normalized built-design graph exporter registered with the JITX CLI."""

import json
from pathlib import Path
from typing import Any, TypedDict

from jitx.component import Component
from jitx.inspect import Trace, visit
from jitx.net import Port
from jitx.plugin.export import Export


def _type_name(value: object) -> str:
    return _class_name(type(value))


def _class_name(value_type: type) -> str:
    return f"{value_type.__module__}.{value_type.__qualname__}"


def _path(trace: Trace) -> str:
    return str(trace.path)


def _captured_geometry(trace: Trace) -> dict[str, str] | None:
    if trace.transform is None:
        return None
    return {
        "type": _type_name(trace.transform),
        "value": str(trace.transform),
    }


@Export.register("bootstrap-graph")
class BootstrapGraphExport(Export):
    """Export a deterministic electrical graph using JITX public APIs."""

    graph: dict[str, Any]

    def submitted(self, design: Any, /, *args: Any, **kwargs: Any) -> None:
        ports: dict[int, dict[str, str]] = {}
        resolved_nets: dict[int, dict[str, Any]] = {}

        for trace, port in design.query(Port):
            port_record = {
                "identity": _path(trace),
                "type": _class_name(Port),
            }
            ports[id(port)] = port_record

            resolved_net = design.nets().find(port)
            if resolved_net is None:
                continue

            net_record = resolved_nets.setdefault(
                id(resolved_net),
                {
                    "name": resolved_net.name,
                    "members": [],
                },
            )
            net_record["members"].append(port_record["identity"])

        components = []
        for trace, component in design.query(Component):
            component_ports = []
            for _, port in visit(component, Port):
                port_record = ports.get(id(port))
                if port_record is not None:
                    component_ports.append(port_record)
            components.append(
                {
                    "identity": _path(trace),
                    "type": _type_name(component),
                    "ports": sorted(component_ports, key=lambda port: port["identity"]),
                }
            )

        nets = [
            {
                "name": record["name"],
                "members": sorted(record["members"]),
            }
            for record in resolved_nets.values()
        ]
        self.graph = {
            "schemaVersion": 1,
            "components": sorted(components, key=lambda component: component["identity"]),
            "ports": sorted(ports.values(), key=lambda port: port["identity"]),
            "nets": sorted(
                nets,
                key=lambda net: (
                    "" if net["name"] is None else net["name"],
                    net["members"],
                ),
            ),
        }

    def export(
        self,
        design: Any,
        /,
        output: Path = Path("parity/bootstrap-graph.json"),
    ) -> None:
        """Write the submitted electrical graph and public capture transforms."""
        geometry = [
            {
                "identity": _path(trace),
                "transform": _captured_geometry(trace),
            }
            for trace, _ in design.query(Component)
        ]
        self.graph["capturedGeometry"] = sorted(geometry, key=lambda item: item["identity"])

        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(self.graph, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


class _ElectricalNetRecord(TypedDict):
    name: str | None
    members: list[str]


class _NamedNetDeclaration(TypedDict):
    identity: str
    name: str
    resolved: bool


@Export.register("m1-electrical-graph")
class M1ElectricalGraphExport(BootstrapGraphExport):
    """Extend C0 capture with electrical metadata; never capture geometry."""

    def submitted(self, design: Any, /, *args: Any, **kwargs: Any) -> None:
        from typing import Protocol, cast

        from jitx.landpattern import PadMapping
        from jitx.net import Net
        from jitx.units import F, ohm

        from he_piantor_42_jitx.components.generic_electrical import Capacitor
        from he_piantor_42_jitx.components.mcu.raspberry_pi_rp2040 import RP2040
        from he_piantor_42_jitx.components.resistor import Resistor

        class SupplierIdentity(Protocol):
            jlcpcb_part_number: str

        super().submitted(design, *args, **kwargs)
        records = {record["identity"]: record for record in self.graph["components"]}
        for trace, component in design.query(Component):
            record = records[_path(trace)]
            record["mpn"] = component.mpn
            record["supplier_part_number"] = (
                cast(SupplierIdentity, component).jlcpcb_part_number if component.mpn else None
            )
            if isinstance(component, Resistor):
                if component.value != component.resistance:
                    raise ValueError(
                        f"Resistor value label disagrees with electrical value: {_path(trace)}"
                    )
                record["value"] = {"unit": "ohm", "magnitude": ohm.m_from(component.resistance)}
            elif isinstance(component, Capacitor):
                if component.value != component.capacitance:
                    raise ValueError(
                        f"Capacitor value label disagrees with electrical value: {_path(trace)}"
                    )
                record["value"] = {"unit": "farad", "magnitude": F.m_from(component.capacitance)}
            else:
                record["value"] = str(component.value) if component.value is not None else None
            record["physical_pin_assignments"] = {}
            if isinstance(component, RP2040):
                # Read actual public pad mappings; the manufacturer owns pad order.
                port_paths = {id(p): _path(t) for t, p in design.query(Port)}
                pin_by_pad = {
                    id(pad): pin
                    for pin, pad in enumerate(component.landpattern.physical_pads(), start=1)
                }
                for _, pad_mapping in visit(component, PadMapping):
                    for port, pad in pad_mapping.items():
                        path = port_paths[id(port)]
                        if path in record["physical_pin_assignments"]:
                            raise ValueError(f"Duplicate RP2040 pad mapping: {path}")
                        record["physical_pin_assignments"][path] = pin_by_pad[id(pad)]
        declarations: list[_NamedNetDeclaration] = []
        groups: dict[int, _ElectricalNetRecord] = {}
        # At submitted(), resolved.name is not yet captured by this runtime.
        # Resolve each public named Net to the SAME runtime connectivity object
        # used by endpoint find(). This binds names without guessing membership.
        for trace, net in design.query(Net):
            if net.name is None:
                continue
            resolved = design.nets().find(net)
            declarations.append(
                {"identity": _path(trace), "name": net.name, "resolved": resolved is not None}
            )
            if resolved is not None:
                group = groups.setdefault(id(resolved), {"name": net.name, "members": []})
                if group["name"] != net.name:
                    raise ValueError(f"Named nets shorted: {group['name']} and {net.name}")
        for trace, port in design.query(Port):
            resolved = design.nets().find(port)
            if resolved is None:
                continue
            group = groups.setdefault(id(resolved), {"name": resolved.name, "members": []})
            group["members"].append(_path(trace))
        self.graph["named_net_declarations"] = sorted(declarations, key=lambda d: d["name"])
        self.graph["nets"] = sorted(
            ({"name": g["name"], "members": sorted(g["members"])} for g in groups.values()),
            key=lambda n: (n["name"] or "", n["members"]),
        )
        self.graph["geometry_excluded"] = True

    def export(
        self,
        design: Any,
        /,
        output: Path = Path("parity/m1-electrical-graph.json"),
    ) -> None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(self.graph, indent=2, sort_keys=True) + "\n", encoding="utf-8")
