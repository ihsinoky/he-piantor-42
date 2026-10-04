"""Retain every raw difference and narrowly classify manufacturing determinism."""

import difflib
import json
import re

from physical.qualify_c4b2 import parse, semantic_pcb
from physical.reproduce_c4b2 import EVIDENCE, OUTPUT, PROJECT, digest


def without_times(path: str, text: str) -> str:
    lines = text.splitlines(keepends=True)
    if path.endswith((".gtl", ".gbl", ".gts", ".gbs", ".gtp", ".gbp", ".gto", ".gbo", ".gm1")):
        return "".join(
            l
            for l in lines
            if not l.startswith(("%TF.CreationDate,", "G04 Created by KiCad (PCBNEW"))
        )
    if path.endswith(".drl"):
        return "".join(
            l
            for l in lines
            if not l.startswith(("; DRILL file {KiCad 9.0.9} date ", "; #@! TF.CreationDate,"))
        )
    if path.endswith("drill-report.txt"):
        return "".join(l for l in lines if not l.startswith("Created on "))
    if path.endswith(".gbrjob"):
        obj = json.loads(text)
        del obj["Header"]["CreationDate"]
        return json.dumps(obj, sort_keys=True)
    if path.endswith("drc.json"):
        obj = json.loads(text)
        del obj["date"]
        return json.dumps(obj, sort_keys=True)
    return text


def sort_independent_flashes(text: str) -> str:
    """Sort only consecutive absolute D03 flashes with unchanged modal state.

    Never reorder paths, apertures, attributes, polarity changes or regions.
    Every flash includes complete X/Y coordinates; duplicate flashes are retained.
    """
    lines, result, flashes = text.splitlines(keepends=True), [], []
    for line in lines:
        if re.fullmatch(r"X-?\d+Y-?\d+D03\*\n", line):
            flashes.append(line)
        else:
            result.extend(sorted(flashes))
            flashes.clear()
            result.append(line)
    result.extend(sorted(flashes))
    return "".join(result)


def main() -> None:
    manifest = json.loads((EVIDENCE / "pipeline.json").read_text())
    first, second = (OUTPUT / f"run-{i}" for i in (1, 2))
    inventories = [r["files"] for r in manifest["runs"]]
    if inventories[0].keys() != inventories[1].keys():
        raise ValueError("Output inventory differs")
    rows = []
    differences = []
    for name in sorted(inventories[0]):
        a, b = (first / name).read_bytes(), (second / name).read_bytes()
        row = {"file": name, "run_1_sha256": digest(a), "run_2_sha256": digest(b)}
        classification = "byte-identical"
        if a != b:
            aa, bb = a.decode(), b.decode()
            diff = list(
                difflib.unified_diff(
                    aa.splitlines(keepends=True),
                    bb.splitlines(keepends=True),
                    fromfile=f"run-1/{name}",
                    tofile=f"run-2/{name}",
                )
            )
            differences.extend(diff)
            classification = "unqualified non-deterministic content"
            if name.endswith(".kicad_pcb"):
                if semantic_pcb(parse(aa)) == semantic_pcb(parse(bb)):
                    classification = (
                        "PCB IDs/order/net-number aliases only; geometry and net names unchanged"
                    )
            elif name.startswith("cam/"):
                aa, bb = without_times(name, aa), without_times(name, bb)
                if aa == bb:
                    classification = "verified timestamp fields only"
                elif name.endswith((".gtl", ".gbl")) and sort_independent_flashes(
                    aa
                ) == sort_independent_flashes(bb):
                    classification = "timestamps and independent via flash ordering only; modal geometry unchanged"
            elif name.endswith((".kicad_sch", ".lib")):
                classification = "schematic companion content differs; PCB/CAM unaffected; schematic semantics unqualified"
            elif name == "runtime-start.log":
                x, y = json.loads(aa), json.loads(bb)
                for k in ("pid", "uri"):
                    x.pop(k)
                    y.pop(k)
                if x == y:
                    classification = "runtime PID and socket URI only"
        row["classification"] = classification
        rows.append(row)
    manufacturing = [
        r
        for r in rows
        if r["file"].startswith("cam/")
        and r["classification"] == "unqualified non-deterministic content"
    ]
    report = {
        "manufacturing_significant_differences": manufacturing,
        "manufacturing_significant_determinism": not manufacturing,
        "comparisons": rows,
        "raw_diff_file": "two-run-differences.json",
        "scope": "Only observed two runs; no general determinism or schematic equivalence claim",
        "analysis_source_sha256": {
            str(p.relative_to(PROJECT)): digest(p.read_bytes())
            for p in sorted((PROJECT / "physical").glob("*c4b2.py"))
        },
    }
    (EVIDENCE / "determinism.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    (EVIDENCE / "two-run-differences.json").write_text(
        json.dumps(
            {
                "encoding": "lossless unified diff lines; decode and join to recover raw whitespace",
                "lines": differences,
            },
            indent=2,
        )
        + "\n"
    )
    if manufacturing:
        raise ValueError("Manufacturing content differs; see determinism.json")
    print(
        "Every raw difference retained; no manufacturing-significant difference in the observed pair"
    )


if __name__ == "__main__":
    main()
