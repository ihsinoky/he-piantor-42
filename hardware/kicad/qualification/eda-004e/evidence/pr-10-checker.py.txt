#!/usr/bin/env python3
"""Verify PCB instances that must exactly retain vendored footprint geometry."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
PCB = Path(__file__).with_name("integrated-sensor-test.kicad_pcb")
RP2040 = Path(__file__).with_name("RP2040_minimal.pretty") / "RP2040-QFN-56.kicad_mod"
HALL = ROOT / "hardware/lib/third_party/marbastlib-he.pretty/SW_MX_HE_0deg_1u.kicad_mod"


def parse(path: Path):
    tokens = re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+', path.read_text())
    pos = 0
    def expression():
        nonlocal pos
        assert tokens[pos] == "("; pos += 1
        result = []
        while tokens[pos] != ")":
            if tokens[pos] == "(": result.append(expression())
            else:
                token = tokens[pos]; pos += 1
                result.append(token[1:-1] if token.startswith('"') else token)
        pos += 1
        return result
    return expression()


def children(node, name):
    return [item for item in node[1:] if isinstance(item, list) and item and item[0] == name]


def child(node, name):
    found = children(node, name)
    return found[0] if found else None


def pad_signature(node):
    def values(name):
        item = child(node, name)
        return tuple(item[1:]) if item else ()
    return (node[1], node[2], node[3], values("at"), values("size"), values("drill"), values("layers"))


def footprint_signature(node):
    pads = sorted(pad_signature(pad) for pad in children(node, "pad"))
    def count_recursive(value, name):
        return (1 if isinstance(value, list) and value and value[0] == name else 0) + sum(
            count_recursive(item, name) for item in value if isinstance(item, list)
        ) if isinstance(value, list) else 0
    return pads, count_recursive(node, "keepout")


def reference(node):
    for prop in children(node, "property"):
        if len(prop) > 2 and prop[1] == "Reference": return prop[2]
    return None


def main():
    board = parse(PCB)
    instances = {reference(fp): fp for fp in children(board, "footprint")}
    expected = {"U1": parse(RP2040), **{f"U{i}": parse(HALL) for i in range(6, 10)}}
    failed = False
    for ref, source in expected.items():
        actual = instances.get(ref)
        if actual is None:
            print(f"FAIL {ref}: instance missing")
            failed = True; continue
        if footprint_signature(actual) != footprint_signature(source):
            ep, ek = footprint_signature(source); ap, ak = footprint_signature(actual)
            print(f"FAIL {ref}: source pads/keepouts={len(ep)}/{ek}, board={len(ap)}/{ak}")
            failed = True
        else: print(f"PASS {ref}: authoritative pad geometry and keepouts match")
    general = child(board, "general"); layers = child(board, "layers")
    thickness = child(general, "thickness") if general else None
    copper = [layer for layer in layers[1:] if isinstance(layer, list) and layer[1].endswith(".Cu")]
    print(f"board: thickness={thickness[1] if thickness else 'missing'} mm, copper_layers={len(copper)}")
    return 1 if failed else 0

if __name__ == "__main__": sys.exit(main())
