"""Normalized built-design graph exporter registered with the JITX CLI."""

import json
from pathlib import Path
from typing import Any

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
