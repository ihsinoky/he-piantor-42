"""Repeat supported C4B generation; write hashes/evidence, never patch artifacts.

Run from hardware/jitx with its activated environment. Restarts the runtime and
deletes only this qualification design's ignored generated state before each run.
Generated packages remain ignored under designs/c4b. The manifest is committed.
This records failure to meet the gate; it does not turn partial routing into PASS.
"""

import hashlib
import json
import re
import shutil
import subprocess
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from parity.m1 import evaluate, load_inputs

PROJECT = Path(__file__).resolve().parents[1]
DESIGN = "he_piantor_42_jitx.physical_qualification.M1FourKeyPhysicalQualification"
ELECTRICAL = "he_piantor_42_jitx.m1.M1FourKeyElectrical"
GENERATED = PROJECT / "designs" / DESIGN
OUTPUT = PROJECT / "designs/c4b"
EVIDENCE = PROJECT / "physical/evidence"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def command(arguments: list[str], log: Path) -> None:
    result = subprocess.run(arguments, cwd=PROJECT, capture_output=True, timeout=90, check=False)
    log.write_bytes(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(f"Command failed ({result.returncode}): {arguments}; see {log}")


def odb_entries(path: Path) -> dict[str, bytes]:
    with ZipFile(path) as archive:
        return {n: archive.read(n) for n in sorted(archive.namelist()) if not n.endswith("/")}


def compare_odb_pnp(entries: dict[str, bytes], placements: list[dict]) -> dict:
    """Read-only independent comparison; ODB angles are clockwise, JITX CCW."""
    components = next(v for k, v in entries.items() if k.endswith("comp_+_top/components"))
    actual = {}
    for line in components.decode().splitlines():
        if line.startswith("CMP "):
            tokens = line.split()
            actual[tokens[6]] = tuple(float(tokens[i]) for i in (2, 3, 4))
    differences = []
    for row in placements:
        expected = (row["x_mm"], row["y_mm"], (-row["rotation_ccw_deg"]) % 360)
        observed = actual.get(row["refdes"])
        if observed is None or any(
            abs(a - b) > 1e-6 for a, b in zip(expected, observed, strict=True)
        ):
            differences.append(row["identity"])
    if len(actual) != len(placements):
        differences.append("component count")
    return {
        "component_count": len(actual),
        "differences": differences,
        "result": "PASS" if not differences else "FAIL",
    }


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    sources = sorted(
        [
            *(PROJECT / "he_piantor_42_jitx").rglob("*.py"),
            *(PROJECT / "physical").rglob("*.py"),
            *(PROJECT / "parity").rglob("*.py"),
            PROJECT / "parity/m1-parity-contract.json",
            PROJECT / "parity/m1-normalization.json",
            PROJECT / "pyproject.toml",
            PROJECT / "uv.lock",
        ]
    )
    source_hashes = {str(p.relative_to(PROJECT)): digest(p.read_bytes()) for p in sources}
    runs = []
    for index in (1, 2):
        run = OUTPUT / f"run-{index}"
        run.mkdir(exist_ok=True)
        command(["jitx", "runtime", "stop"], run / "runtime-stop.log")
        if GENERATED.exists():
            shutil.rmtree(GENERATED)
        command(["jitx", "runtime", "start", "--background"], run / "runtime-start.log")
        command(["jitx", "design", "build", DESIGN, "--no-dependency-check"], run / "build.log")
        command(
            ["jitx", "design", "export", "physical-qualification", DESIGN, "--output", str(run)],
            run / "capture.log",
        )
        command(["jitx", "design", "export", "legacy-odb++", DESIGN], run / "odb.log")
        shutil.copyfile(GENERATED / "outputs/odb.zip", run / "odb.zip")
        observation = json.loads((run / "physical-observation.json").read_text())
        entries = odb_entries(run / "odb.zip")
        pnp = compare_odb_pnp(entries, observation["placements"])
        if pnp["result"] != "PASS":
            raise ValueError(f"ODB/PnP disagreement: {pnp}")
        if observation["inter_component_pad_overlaps"] or observation["pads_outside_board"]:
            raise ValueError("Qualification placement overlaps or extends outside board")
        if len(observation["placements"]) != 68 or not all(
            r["realized"] for r in observation["routes"]
        ):
            raise ValueError("Missing placement or source-route realization")
        runs.append(
            {
                "run": index,
                "placement_count": len(observation["placements"]),
                "realized_route_count": len(observation["routes"]),
                "route_layers": sorted({r["layer"] for r in observation["routes"]}),
                "via_count": len(observation["vias"]),
                "odb_pnp_comparison": pnp,
                "files": {
                    p.name: digest(p.read_bytes())
                    for p in sorted(run.iterdir())
                    if p.is_file() and p.suffix != ".log"
                },
                "odb_entries": {n: digest(v) for n, v in entries.items()},
            }
        )
    if source_hashes != {str(p.relative_to(PROJECT)): digest(p.read_bytes()) for p in sources}:
        raise ValueError("Source changed during repeated generation")
    comparisons = []
    for name, first in runs[0]["files"].items():
        second = runs[1]["files"][name]
        comparisons.append(
            {
                "file": name,
                "run_1_sha256": first,
                "run_2_sha256": second,
                "classification": "identical" if first == second else "non-deterministic content",
            }
        )
    odb_comparison = []
    first_entries, second_entries = (odb_entries(OUTPUT / f"run-{i}/odb.zip") for i in (1, 2))
    for name in sorted(first_entries.keys() | second_entries.keys()):
        first, second = first_entries.get(name), second_entries.get(name)
        classification = "identical" if first == second else "non-deterministic content"
        # Only known time fields are metadata; everything else stays unqualified.
        if first != second and first is not None and second is not None and name == "misc/info":

            def without_times(data: bytes) -> list[bytes]:
                return [
                    line
                    for line in data.splitlines()
                    if not line.startswith((b"CREATION_DATE=", b"SAVE_DATE="))
                ]

            if without_times(first) == without_times(second):
                classification = "deterministic metadata difference only"
        entry = {"file": name, "classification": classification}
        if first is not None and second is not None and name.endswith(("/features", "/netlist")):
            # Narrow read-only comparison: no claim that all ODB ID cross-links
            # are equivalent. Retain raw differences and all geometric values.
            def records(data: bytes) -> Counter:
                return Counter(re.sub(rb";ID=\d+", b"", data).splitlines())

            entry["unordered_records_excluding_feature_ids_equal"] = records(first) == records(
                second
            )
        odb_comparison.append(entry)
    command(
        [
            "jitx",
            "design",
            "export",
            "m1-electrical-graph",
            ELECTRICAL,
            "--output",
            str(OUTPUT / "c2-regression.json"),
        ],
        OUTPUT / "c2.log",
    )
    raw = json.loads((OUTPUT / "c2-regression.json").read_text())
    contract, mapping = load_inputs()
    _, parity = evaluate(raw, contract, mapping)
    if parity["result"] != "PASS":
        raise ValueError(parity)
    # Compare only the original circuit endpoints; physical via ports are extra
    # geometric attachments, explicitly excluded from this topology comparison.
    wrapper = json.loads((OUTPUT / "run-2/electrical-graph.json").read_text())
    component_ports = {p["identity"] for c in raw["components"] for p in c["ports"]}

    def component_nets(graph: dict) -> list:
        return sorted(
            [
                (n["name"] or "", sorted(set(n["members"]) & component_ports))
                for n in graph["nets"]
                if set(n["members"]) & component_ports
            ]
        )

    if raw["components"] != wrapper["components"] or component_nets(raw) != component_nets(wrapper):
        raise ValueError("Physical wrapper changed original component topology")
    # Endpoint accounting is conservative: route experiment connects only Hall
    # OUT/probe pairs; the mux endpoint on each same net is still unrouted.
    accounting = []
    for net in raw["nets"]:
        members = sorted(set(net["members"]) & component_ports)
        accounting.append(
            {
                "net": net["name"],
                "component_endpoints": members,
                "routing_status": "partial: Hall OUT/probe only"
                if net["name"] in {"H0_RAW", "H1_RAW", "H2_RAW", "H3_RAW"}
                else "no source routes; singleton requires physical pad review"
                if len(members) == 1
                else "unrouted",
            }
        )
    manifest = {
        "schema_version": 1,
        "issue": 43,
        "verdict": "BLOCKED",
        "source_sha256": source_hashes,
        "runs": runs,
        "comparisons": comparisons,
        "odb_entry_comparisons": odb_comparison,
        "electrical_parity": parity,
        "wrapper_component_topology_preserved": True,
        "endpoint_routing_accounting": accounting,
        "unconnected_component_endpoints": sorted(
            component_ports - {p for net in raw["nets"] for p in net["members"]}
        ),
        "mandatory_gerber_excellon": "not generated: no supported direct workflow established",
        "full_routing_complete": False,
        "full_drc_pass": False,
    }
    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / "build-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    print(
        "Recorded C4B BLOCKED evidence; C2 parity PASS; partial two-layer copper and ODB++ generated twice."
    )


if __name__ == "__main__":
    main()
