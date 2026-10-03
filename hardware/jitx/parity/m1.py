"""Strict, geometry-free normalization and comparison of exported runtime graphs."""

import argparse
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_inputs() -> tuple[dict, dict]:
    return (
        json.loads((ROOT / "m1-parity-contract.json").read_text()),
        json.loads((ROOT / "m1-normalization.json").read_text()),
    )


def normalize(raw: dict, mapping: dict, contract: dict) -> dict:
    """Only explicit identities are accepted; no suffix/fuzzy matching."""
    components = mapping["components"]
    aliases = {}
    for record in components.values():
        for physical, semantic in record["ports"].items():
            if physical in aliases or semantic in aliases.values():
                raise ValueError(f"Duplicate endpoint alias: {physical} -> {semantic}")
            aliases[physical] = semantic
    expected = {
        f"{ref}.{port}"
        for ref, ports in contract["structured_graph"]["component_port_identities"].items()
        for port in ports
    }
    if set(aliases.values()) != expected:
        raise ValueError("Normalization aliases do not cover the frozen endpoints exactly")
    references = [record["reference"] for record in components.values()]
    if len(set(references)) != len(references):
        raise ValueError("Duplicate normalized component references")
    extras = mapping["extra_unconnected_endpoints"]
    if len(set(extras)) != len(extras) or set(extras) & set(aliases):
        raise ValueError("Duplicate/overlapping extra endpoint inventory")
    allowed = set(aliases) | set(extras)
    identities = [port["identity"] for port in raw["ports"]]
    if len(set(identities)) != len(identities):
        raise ValueError("Duplicate built endpoint identity")
    if set(identities) != allowed:
        raise ValueError(
            f"Built endpoint inventory: missing={sorted(allowed - set(identities))}; "
            f"unknown={sorted(set(identities) - allowed)}"
        )
    built_components = [c["identity"] for c in raw["components"]]
    if Counter(built_components) != Counter(components.keys()):
        raise ValueError(f"Built component population differs: {built_components}")
    result = []
    for component in raw["components"]:
        identity = component["identity"]
        ports = [p["identity"] for p in component["ports"]]
        if component["type"] != components[identity]["expected_type"]:
            raise ValueError(
                f"{identity}: expected accepted model {components[identity]['expected_type']}, got {component['type']}"
            )
        assignments = component["physical_pin_assignments"]
        if components[identity]["reference"] == "U_MCU":
            if set(assignments) != set(ports) or set(assignments.values()) != set(range(1, 58)):
                raise ValueError("RP2040 physical pin inventory is missing/unknown/duplicated")
        elif assignments:
            raise ValueError(f"Unexpected physical signal mapping for {identity}")
        required = set(components[identity]["ports"])
        extra = {p for p in extras if p.rsplit(".", 1)[0] == identity}
        if set(ports) != required | extra or len(set(ports)) != len(ports):
            raise ValueError(f"Component {identity} has missing/unknown/duplicate ports")
        result.append(
            {
                "reference": components[identity]["reference"],
                "type": component["type"],
                "ports": sorted(aliases[p] for p in ports if p in aliases),
                "mpn": component["mpn"],
                "supplier_part_number": component["supplier_part_number"],
                "value": component["value"],
                "physical_pin_assignments": {
                    aliases[p]: pin
                    for p, pin in component["physical_pin_assignments"].items()
                    if p in aliases
                },
            }
        )
    nets = []
    membership = set()
    for net in raw["nets"]:
        members = net["members"]
        if len(set(members)) != len(members) or membership & set(members):
            raise ValueError(f"Duplicate net membership: {members}")
        membership.update(members)
        if set(members) - allowed:
            raise ValueError(f"Unknown net endpoints: {members}")
        if set(members) & set(extras):
            raise ValueError(f"Unused physical RP2040 GPIO is connected: {members}")
        nets.append({"name": net["name"], "members": sorted(aliases[p] for p in members)})
    return {
        "schema_version": 1,
        "geometry_excluded": True,
        "components": sorted(result, key=lambda c: c["reference"]),
        "endpoints": sorted(aliases.values()),
        "extra_unconnected_endpoints": sorted(extras),
        "nets": sorted(nets, key=lambda n: (n["name"] or "", n["members"])),
        "named_net_declarations": raw["named_net_declarations"],
    }


def compare(graph: dict, contract: dict, mapping: dict) -> dict:
    """Compare all memberships, including unexpected shorts and extra edges."""
    frozen = contract["structured_graph"]
    differences = []
    expected_ports = frozen["component_port_identities"]
    built = {c["reference"]: c for c in graph["components"]}
    if Counter(c["reference"] for c in graph["components"]) != Counter(expected_ports.keys()):
        differences.append("Component population differs from frozen references")
    for ref, ports in expected_ports.items():
        expected = {f"{ref}.{p}" for p in ports}
        if ref not in built or set(built[ref]["ports"]) != expected:
            differences.append(f"{ref}: normalized port inventory differs")
    all_expected = {f"{ref}.{p}" for ref, ports in expected_ports.items() for p in ports}
    if Counter(graph["endpoints"]) != Counter(all_expected):
        differences.append("Normalized global endpoint inventory differs")
    declarations = graph["named_net_declarations"]
    if Counter(d["name"] for d in declarations) != Counter(frozen["expected_nets"]):
        differences.append("Named net declaration inventory differs")
    for d in declarations:
        if not d["resolved"]:
            differences.append(f"Named net {d['name']} does not resolve")
    names = [n["name"] for n in graph["nets"] if n["name"] is not None]
    # Empty CC1/CC2 declarations must resolve but have no golden endpoint edges.
    expected_named_members = {n: set() for n in frozen["expected_nets"]}
    for edge in frozen["endpoint_to_net_edges"]:
        expected_named_members[edge["net"]].add(edge["endpoint"])
    actual_named_members = {}
    actual_groups = []
    for net in graph["nets"]:
        members = set(net["members"])
        actual_groups.append(frozenset(members))
        if net["name"] is not None:
            if net["name"] in actual_named_members:
                differences.append(f"Duplicate resolved named net: {net['name']}")
            actual_named_members[net["name"]] = members
    for name, expected in expected_named_members.items():
        actual = actual_named_members.get(name)
        if actual != expected:
            differences.append(
                f"Net {name}: missing={sorted(expected - (actual or set()))}; "
                f"unexpected={sorted((actual or set()) - expected)}; exists={actual is not None}"
            )
    unexpected_names = set(names) - set(expected_named_members)
    if unexpected_names:
        differences.append(f"Unexpected named nets: {sorted(unexpected_names)}")
    expected_groups = [frozenset(m) for m in expected_named_members.values()]
    for link in frozen["direct_endpoint_links"]:
        group = frozenset(link["endpoints"])
        expected_groups.append(group)
        if group not in actual_groups:
            differences.append(f"Direct link missing or shorted: {sorted(group)}")
    if Counter(actual_groups) != Counter(expected_groups):
        differences.append("Connectivity group inventory differs (extra net, short, or open)")
    connected = {p for n in graph["nets"] for p in n["members"]}
    for endpoint in frozen["intentional_no_connect_endpoints"]:
        if endpoint in connected:
            differences.append(f"Intentional NC connected: {endpoint}")
    required_connected = all_expected - set(frozen["intentional_no_connect_endpoints"])
    for endpoint in sorted(required_connected - connected):
        differences.append(f"Expected connected endpoint floats: {endpoint}")
    active = []
    for entry in contract["active_components"]:
        refs = [entry["reference"]] if "reference" in entry else ["U_H0", "U_H1", "U_H2", "U_H3"]
        for ref in refs:
            active.append(ref)
            component = built.get(ref, {})
            for key, source in [
                ("mpn", "manufacturer_part_number"),
                ("supplier_part_number", "supplier_part_number"),
            ]:
                if component.get(key) != entry[source]:
                    differences.append(
                        f"{ref}: {key} expected {entry[source]}, got {component.get(key)}"
                    )
    # Each passive group points to one exact frozen key/value, not mutable expected numbers.
    seen_passives = []
    quantities = {
        "5.1 kOhm": ("ohm", 5100),
        "27 Ohm": ("ohm", 27),
        "1 kOhm": ("ohm", 1000),
        "6.8 kOhm": ("ohm", 6800),
        "10 kOhm": ("ohm", 10000),
        "1.5 kOhm": ("ohm", 1500),
        "1 nF": ("farad", 1e-9),
        "15 pF": ("farad", 15e-12),
        "100 nF on V3V3": ("farad", 100e-9),
        "100 nF on V1V1": ("farad", 100e-9),
        "100 nF": ("farad", 100e-9),
        "1 uF": ("farad", 1e-6),
        "10 uF": ("farad", 10e-6),
    }
    groups = mapping["passive_value_groups"]
    frozen_values = contract["component_population"]["passive_values"]
    if set(groups) != set(frozen_values):
        differences.append("Passive group coverage differs from frozen contract")
    for key, refs in groups.items():
        unit, magnitude = quantities[frozen_values[key]]
        for ref in refs:
            seen_passives.append(ref)
            value = built.get(ref, {}).get("value")
            if (
                not isinstance(value, dict)
                or value.get("unit") != unit
                or not math.isclose(
                    value.get("magnitude", math.nan), magnitude, rel_tol=1e-12, abs_tol=0
                )
            ):
                differences.append(f"{ref}: expected {magnitude} {unit}, got {value}")
    passive_refs = {ref for ref in expected_ports if ref.startswith(("R_", "C_"))}
    if Counter(seen_passives) != Counter(passive_refs):
        differences.append("Passive references missing/duplicated in group mapping")
    for ref in set(expected_ports) - set(active):
        if built.get(ref, {}).get("mpn") or built.get(ref, {}).get("supplier_part_number"):
            differences.append(f"{ref}: generic component claims manufacturer/supplier identity")
    expected_pins = {f"U_MCU.{p}": n for p, n in contract["rp2040"]["physical_pin_mapping"].items()}
    if built.get("U_MCU", {}).get("physical_pin_assignments") != expected_pins:
        differences.append("RP2040 normalized logical-to-physical pin assignments differ")
    return {
        "result": "FAIL" if differences else "PASS",
        "compared_component_count": len(expected_ports),
        "compared_endpoint_count": len(all_expected),
        "compared_named_net_count": len(frozen["expected_nets"]),
        "compared_edge_count": len(frozen["endpoint_to_net_edges"]),
        "direct_link_count": len(frozen["direct_endpoint_links"]),
        "intentional_nc_count": len(frozen["intentional_no_connect_endpoints"]),
        "differences": differences,
        "geometry_excluded": True,
        "note": "Electrical semantics only. Geometry parity NOT established; HRO/Winbond reconciliation deferred to EDA-002C3.",
    }


def evaluate(raw: dict, contract: dict, mapping: dict) -> tuple[dict | None, dict]:
    try:
        graph = normalize(raw, mapping, contract)
        return graph, compare(graph, contract, mapping)
    except (ValueError, KeyError, TypeError) as error:
        return None, {"result": "FAIL", "differences": [str(error)], "geometry_excluded": True}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph", type=Path, help="Raw m1-electrical-graph runtime export")
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--normalized", type=Path, required=True)
    args = parser.parse_args()
    contract, mapping = load_inputs()
    graph, result = evaluate(json.loads(args.graph.read_text()), contract, mapping)
    args.result.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if graph is not None:
        args.normalized.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["result"] == "PASS" else 1)


if __name__ == "__main__":
    main()
