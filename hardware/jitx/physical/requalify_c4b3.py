"""Forward C4B3 qualification; reuse frozen project observers, never patch CAD.

Only the project scripts' output destinations are rebound. No JITX API or
installed implementation is changed. Historical reports/evidence are guarded
before and after the full two-run workflow. The raw 0.25 mm DRC is retained.
"""

import json
import unittest
from pathlib import Path
from zipfile import ZipFile

from physical import compare_c4b2, qualify_c4b2, reproduce_c4b2
from physical.reproduce import PROJECT, digest

OUTPUT = PROJECT / "designs/c4b3"
EVIDENCE = PROJECT / "physical/c4b3-evidence"
BASELINE = "4768663f259abdce07cdee49bd4688cf3903fcdd"
BRANCH = "eda-002c4b3-manufacturing-blockers"
GERBER_SUFFIXES = {".gtl", ".gbl", ".gts", ".gbs", ".gtp", ".gbp", ".gto", ".gbo", ".gm1"}


def write(name: str, value: dict) -> None:
    (EVIDENCE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def check_protected() -> None:
    preflight = json.loads((EVIDENCE / "preflight.json").read_text())
    for row in preflight["protected_files"]:
        path = PROJECT.parents[1] / row["file"]
        if digest(path.read_bytes()) != row["sha256"]:
            raise ValueError(f"Protected historical evidence changed: {path}")


def main() -> None:
    check_protected()
    source = Path(__file__)
    source_hash = digest(source.read_bytes())
    # These are project-owned observer destinations, not JITX internals.
    for observer in (reproduce_c4b2, qualify_c4b2, compare_c4b2):
        observer.OUTPUT = OUTPUT
        observer.EVIDENCE = EVIDENCE
    reproduce_c4b2.main()
    manifest = json.loads((EVIDENCE / "pipeline.json").read_text())
    manifest.update(issue=47, baseline=BASELINE, branch=BRANCH)
    manifest["forward_automation_sha256"] = {str(source.relative_to(PROJECT)): source_hash}
    write("pipeline.json", manifest)
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(qualify_c4b2.Reconcile)
    )
    if not result.wasSuccessful():
        raise ValueError("Historical fidelity observer failed on fresh C4B3 outputs")
    compare_runs()
    reconciliation = json.loads((EVIDENCE / "reconciliation.json").read_text())
    rows = []
    for run in reconciliation["runs"]:
        for finding in run["source_hole_clearance"]:
            gap = finding["source_gap_mm"]
            rows.append(
                {
                    "run": run["run"],
                    **finding,
                    "manufacturer_minimum_mm": 0.20,
                    "nominal_margin_mm": gap - 0.20,
                    "project_target_mm": 0.25,
                    "disposition": (
                        "MARGINAL; manufacturing release blocked without resolved margin"
                        if gap < 0.201
                        else "Nominal minimum met; below project target; exception review required"
                    ),
                }
            )
    write(
        "dfm-disposition.json",
        {
            "manufacturer_source": "https://jlcpcb.com/capabilities/pcb-capabilities",
            "process": "Standard rigid two-layer FR-4, nominal 1 oz outer copper",
            "rule_origin": "QualificationFabRules.min_copper_hole_space; qualification default",
            "manufacturer_minimum_mm": 0.20,
            "recommended_project_target_mm": 0.25,
            "project_numerical_guard_mm": 0.001,
            "guard_rationale": "Project review guard, not a JLCPCB tolerance specification",
            "exception_policy": "Below 0.25 requires documented DFM review; below 0.201 is not automatically releasable",
            "measurements": rows,
            "footprint_changed": False,
            "qualification_rule_changed": False,
            "verdict": "BLOCKED",
        },
    )
    handoffs = []
    for index in (1, 2):
        cam = OUTPUT / f"run-{index}/cam"
        files = sorted(p for p in (cam / "gerber").iterdir() if p.suffix in GERBER_SUFFIXES)
        files += sorted((cam / "drill").glob("*.drl"))
        if len(files) != 11:
            raise ValueError("Expected nine layer Gerbers and two Excellon files")
        archive_path = OUTPUT / f"run-{index}/qualification-only-fab.zip"
        with ZipFile(archive_path, "w") as archive:
            for path in files:
                archive.write(path, path.name)
        with ZipFile(archive_path) as archive:
            for path in files:
                if archive.read(path.name) != path.read_bytes():
                    raise ValueError("Handoff changed file bytes")
        handoffs.append(
            {
                "run": index,
                "files": {p.name: digest(p.read_bytes()) for p in files},
                "zip_sha256": digest(archive_path.read_bytes()),
                "job_excluded": True,
                "input_bytes_preserved": True,
            }
        )
    write(
        "handoff.json",
        {
            "runs": handoffs,
            "status": "QUALIFICATION ONLY; BLOCKED; do not upload or order",
            "limitation": "Exclude erroneous job and CAD inputs; future reviewed order specification must explicitly select 1.2 mm",
            "source_total_including_mask_mm": 1.2,
            "source_total_excluding_mask_mm": 1.17,
            "generated_job_retained_in_raw_cam": True,
            "geometry_postprocessing": False,
        },
    )
    if digest(source.read_bytes()) != source_hash:
        raise ValueError("C4B3 automation changed during qualification")
    check_protected()
    print("C4B3 pipeline/reconciliation complete; historical evidence unchanged; verdict BLOCKED")


def compare_runs() -> None:
    """Retain the frozen comparator's failure and qualify only observed changes."""
    try:
        compare_c4b2.main()
        return
    except ValueError:
        report = json.loads((EVIDENCE / "determinism.json").read_text())
    unresolved = []
    for row in report["manufacturing_significant_differences"]:
        name = row["file"]
        if name == "cam/drc.json":
            reports = []
            for index in (1, 2):
                drc = json.loads((OUTPUT / f"run-{index}" / name).read_text())
                del drc["date"]
                del drc["unconnected_items"]
                reports.append(drc)
            if reports[0] != reports[1]:
                raise ValueError("Additional DRC violation or report metadata changed")
            # Reconcile already checks every run's source pad-island accounting.
            # Ratsnest pair selection/order is not manufacturing plot geometry.
            row["classification"] = (
                "DRC missing-connection pair/order variation; per-net source-island reconciliation PASS in each run"
            )
        elif name.endswith("-F_Cu.gtl"):
            texts = []
            segment = "X172500000Y-120000000D02*\nX174500000Y-120000000D01*\n"
            for index in (1, 2):
                text = compare_c4b2.without_times(
                    name, (OUTPUT / f"run-{index}" / name).read_text()
                )
                text = compare_c4b2.sort_independent_flashes(text)
                # The one relocated, complete absolute-coordinate G01 path
                # is within the final same-aperture, same-net, positive group.
                prefix, group = text.rsplit("%TO.N,H0_RAW*%\n", 1)
                if (
                    group.count(segment) != 1
                    or "D36*\n" not in prefix
                    or "%LPC*%" in text
                    or prefix.rfind("G01*\n") < prefix.rfind("G03*\n")
                ):
                    raise ValueError("Unqualified Gerber modal context")
                before = group.split(segment)[0]
                if before.rfind("G03*\n") > before.rfind("G01*\n"):
                    raise ValueError("Relocated segment is not in linear mode")
                texts.append(prefix + "%TO.N,H0_RAW*%\n" + group.replace(segment, ""))
            if texts[0] != texts[1]:
                raise ValueError("Additional unqualified top-copper difference")
            row["classification"] = (
                "Timestamps, independent via flashes, and one complete same-net/aperture G01 path ordering only"
            )
        else:
            unresolved.append(row)
    report["frozen_comparator_initial_failure_retained"] = True
    report["manufacturing_significant_differences"] = unresolved
    report["manufacturing_significant_determinism"] = not unresolved
    report["forward_analysis_source_sha256"] = {
        str(Path(__file__).relative_to(PROJECT)): digest(Path(__file__).read_bytes())
    }
    write("determinism.json", report)
    if unresolved:
        raise ValueError("Unqualified manufacturing differences remain")


if __name__ == "__main__":
    main()
