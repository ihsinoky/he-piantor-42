#!/usr/bin/env python3
"""Extract and classify footprint dependencies from the integrated schematic."""

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCHEMATIC = ROOT / "hardware/sensor-test/kicad/integrated-sensor-test.kicad_sch"
TABLE = ROOT / "hardware/sensor-test/kicad/fp-lib-table"
INVENTORY = ROOT / "hardware/sensor-test/kicad/footprint-dependencies.json"
OFFICIAL_LIBRARIES = {
    "Capacitor_SMD", "Connector_PinHeader_2.54mm", "Connector_USB", "Crystal",
    "LED_SMD", "MountingHole", "Package_SO", "Package_TO_SOT_SMD",
    "Resistor_SMD", "TestPoint",
}


def inventory() -> dict[str, object]:
    schematic_text = SCHEMATIC.read_text(encoding="utf-8")
    references = sorted(set(re.findall(r'\(property "Footprint" "([^"]+)"', schematic_text)))
    table_text = TABLE.read_text(encoding="utf-8")
    local_libraries = set(re.findall(r'\(name\s+([^\s\)]+)\)', table_text))

    local, official, unresolved = [], [], []
    for reference in references:
        library, separator, _ = reference.partition(":")
        if not separator:
            unresolved.append(reference)
        elif library in local_libraries:
            local.append(reference)
        elif library in OFFICIAL_LIBRARIES:
            official.append(reference)
        else:
            unresolved.append(reference)

    return {
        "schematic": str(SCHEMATIC.relative_to(ROOT)),
        "already_repo_local": local,
        "kicad_standard_requiring_vendoring": official,
        "unresolved": unresolved,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="check the committed inventory")
    args = parser.parse_args()
    result = inventory()
    rendered = json.dumps(result, indent=2) + "\n"
    if args.check:
        if INVENTORY.read_text(encoding="utf-8") != rendered:
            print(f"{INVENTORY.relative_to(ROOT)} is stale; regenerate it with {Path(__file__).name}")
            return 1
        if result["unresolved"]:
            print("Unresolved footprint references:", *result["unresolved"], sep="\n  ")
            return 1
        print(f"Verified {sum(len(result[key]) for key in ('already_repo_local', 'kicad_standard_requiring_vendoring'))} footprint references; unresolved = 0")
        return 0
    INVENTORY.write_text(rendered, encoding="utf-8")
    print(f"Wrote {INVENTORY.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
