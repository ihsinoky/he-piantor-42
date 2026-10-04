"""Bounded read-only coupon observer and byte-preserving human-upload packager.

Gerber observation supports this fixture's positive absolute 4.6-mm flashes,
KiCad outline macros and oval apertures only; unexpected copper syntax fails.
It is not a general Gerber interpreter or a manufacturing release check.
"""

import json
import math
import re
import unittest
from collections import Counter
from zipfile import ZIP_STORED, ZipFile, ZipInfo

from jitx.substrate import SubstrateContext
from jitx.test import TestCase
from shapely import affinity, wkt
from shapely.geometry import LineString, Polygon

from he_piantor_42_jitx.physical_qualification import QualificationSubstrate
from he_piantor_42_jitx.usb_dfm_coupon import CouponCircuit
from physical.compare_c4b2 import without_times
from physical.measure_c4b4a import gap
from physical.qualify_c4b2 import node, nodes, pad_geometry, parse, semantic_pcb
from physical.reproduce import digest
from physical.reproduce_c4b4a import DESIGN, EVIDENCE, OUTPUT, PROJECT, protected, write

GERBERS = {".gtl", ".gbl", ".gts", ".gbs", ".gtp", ".gbp", ".gto", ".gbo", ".gm1"}
ZIP_PATH = OUTPUT / "USB-NPTH-DFM-TEST-ONLY-DO-NOT-ORDER-HUMAN-UPLOAD.zip"


def local(x, y):
    # Qualified legacy-export page offset; coupon source datum is (0, -5).
    return x - 139.5, y + 113.0


def copper_flashes(text):
    """Observe every copper command; reject all unqualified geometry/modal forms."""
    required = ("%MOMM*%", "%FSLAX46Y46*%", "%LPD*%", "%TF.FilePolarity,Positive*%")
    if any(s not in text for s in required):
        raise ValueError("Unqualified copper coordinate/polarity format")
    macros = {}
    for name, body in re.findall(r"%AM([^*]+)\*\n([^%]+)\*%", text):
        values = body.split(",")
        if values[:2] != ["4", "1"] or values[-1] != "$1":
            raise ValueError("Unqualified aperture macro")
        count = int(values[2])
        coords = list(map(float, values[3:-1]))
        if len(coords) != 2 * (count + 1):
            raise ValueError("Aperture outline vertex count differs")
        macros[name] = Polygon(list(zip(coords[::2], coords[1::2], strict=True)))
    apertures = {}
    for code, kind, params in re.findall(r"%ADD(\d+)([^,*]+),([^*]+)\*%", text):
        if kind in macros:
            if float(params) != 0:
                raise ValueError("Unqualified aperture rotation")
            apertures[code] = macros[kind]
        elif kind == "O":
            width, height = map(float, params.split("X"))
            radius = min(width, height) / 2
            half = abs(width - height) / 2
            ends = [(-half, 0), (half, 0)] if width > height else [(0, -half), (0, half)]
            apertures[code] = LineString(ends).buffer(radius, quad_segs=128)
        else:
            raise ValueError(f"Unqualified aperture type: {kind}")
    body = text.split("G04 APERTURE END LIST*\n", 1)[1]
    aperture, pad = None, None
    flashes = {}
    for line in body.splitlines():
        if match := re.fullmatch(r"D(\d+)\*", line):
            aperture = match[1]
        elif match := re.fullmatch(r"%TO.P,J1,([^*]+)\*%", line):
            pad = match[1]
        elif match := re.fullmatch(r"X(-?\d+)Y(-?\d+)D03\*", line):
            if pad is None or pad in flashes or aperture not in apertures:
                raise ValueError("Missing/duplicate flash identity or aperture")
            x, y = local(*(int(v) / 1e6 for v in match.groups()))
            flashes[pad] = affinity.translate(apertures[aperture], x, y)
        elif line.startswith("%TO.N,") or line in ("%TD*%", "M02*"):
            continue
        else:
            raise ValueError(f"Unqualified copper command: {line}")
    return flashes


def drills(text):
    if "METRIC\n" not in text or "G90\n" not in text:
        raise ValueError("Unqualified drill coordinate format")
    tools, hits = {}, []
    tool = None
    for line in text.splitlines():
        if match := re.fullmatch(r"T(\d+)C([\d.]+)", line):
            tools[match[1]] = float(match[2])
        elif match := re.fullmatch(r"T(\d+)", line):
            tool = match[1]
        elif line.startswith("X"):
            if not re.fullmatch(r"X-?[\d.]+Y-?[\d.]+(?:G85X-?[\d.]+Y-?[\d.]+)?", line):
                raise ValueError("Unqualified Excellon hit")
            values = [float(v) for v in re.findall(r"[XY](-?[\d.]+)", line)]
            coords = [local(*values[i : i + 2]) for i in range(0, len(values), 2)]
            hits.append([tools[tool], *[v for pair in coords for v in pair]])
        elif line.startswith(";") or line in ("M48", "FMAT,2", "METRIC", "%", "G90", "G05", "M30"):
            continue
        else:
            raise ValueError(f"Unqualified drill command: {line}")
    return sorted(hits)


class Reconcile(TestCase):
    def test_fidelity_and_package(self):
        protected()
        source = json.loads((EVIDENCE / "source-measurements.json").read_text())
        tolerance = source["observer_tolerance_mm"]
        with SubstrateContext(QualificationSubstrate()):
            connector = CouponCircuit().J_USB
            expected_pth = []
            for shell in connector.landpattern.shell:
                bounds = (shell.transform * shell.cutout.shape).to_shapely().bounds
                radius = (bounds[2] - bounds[0]) / 2
                x = (bounds[0] + bounds[2]) / 2
                expected_pth.append([2 * radius, x, bounds[1] + radius, x, bounds[3] - radius])
        results, boards, fabrication = [], [], []
        for index in (1, 2):
            run = OUTPUT / f"run-{index}"
            pcb_path = run / "kicad" / f"{DESIGN}.kicad_pcb"
            pcb = parse(pcb_path.read_text())
            boards.append(semantic_pcb(pcb))
            footprints = nodes(pcb, "footprint")
            self.assertEqual(len(footprints), 1)
            fp = footprints[0]
            self.assertEqual(list(map(float, node(fp, "at"))), [139.5, 113, 0])
            self.assertEqual(node(fp, "layer"), ["F.Cu"])
            self.assertFalse(
                nodes(pcb, "segment") + nodes(pcb, "arc") + nodes(pcb, "via") + nodes(pcb, "zone")
            )
            self.assertEqual(len(nodes(fp, "pad")), 20)
            pads = {
                p[1]: p
                for p in nodes(fp, "pad")
                if set(node(p, "layers")) & {"F.Cu", "B.Cu", "*.Cu"}
            }
            self.assertEqual(len(pads), 16)
            pcb_distances = []
            for row in source["all_copper_pads"]:
                name = re.sub(r"\[(\d+)\]", r"\1", row["path"].split(".")[-1])
                actual = affinity.translate(pad_geometry(pads[name], fp), yoff=5)
                distance = wkt.loads(row["wkt_mm"]).hausdorff_distance(actual)
                self.assertLess(distance, tolerance)
                pcb_distances.append({"pad": name, "hausdorff_mm": distance})
            text = pcb_path.read_text()
            self.assertIn('"DFM TEST ONLY"', text)
            self.assertIn('"DO NOT ORDER"', text)
            cam = run / "cam"
            files = sorted(p for p in (cam / "gerber").iterdir() if p.suffix in GERBERS)
            files += sorted((cam / "drill").glob("*.drl"))
            self.assertEqual(
                Counter(p.suffix for p in files), Counter({**{s: 1 for s in GERBERS}, ".drl": 2})
            )
            for p in files[:9]:
                self.assertIn("%MOMM*%", p.read_text())
            top = copper_flashes(next(p for p in files if p.suffix == ".gtl").read_text())
            bottom = copper_flashes(next(p for p in files if p.suffix == ".gbl").read_text())
            self.assertEqual(set(top), set(pads))
            self.assertEqual(set(bottom), {f"shell{i}" for i in range(4)})
            comparisons = []
            for row in source["all_copper_pads"]:
                name = re.sub(r"\[(\d+)\]", r"\1", row["path"].split(".")[-1])
                expected = wkt.loads(row["wkt_mm"])
                for side, actual in [("top", top[name])] + (
                    [("bottom", bottom[name])] if name in bottom else []
                ):
                    distance = expected.hausdorff_distance(actual)
                    self.assertLess(distance, tolerance)
                    comparisons.append(
                        {
                            "pad": name,
                            "side": side,
                            "hausdorff_mm": distance,
                            "gerber_bounds_mm": list(actual.bounds),
                        }
                    )
            npth_path = next(p for p in files if "-NPTH.drl" in p.name)
            pth_path = next(p for p in files if "-PTH.drl" in p.name)
            self.assertIn("TF.FileFunction,NonPlated,1,2,NPTH", npth_path.read_text())
            self.assertIn("TF.FileFunction,Plated,1,2,PTH", pth_path.read_text())
            npth, pth = drills(npth_path.read_text()), drills(pth_path.read_text())
            expected_npth = sorted([h["diameter_mm"], *h["center_mm"]] for h in source["npth"])
            self.assertEqual(len(npth), 2)
            self.assertEqual(len(pth), 4)
            for expected, actual in zip(sorted(expected_pth), pth, strict=True):
                self.assertEqual(len(expected), len(actual))
                for a, b in zip(expected, actual, strict=True):
                    self.assertLess(abs(a - b), 1e-6)
            for expected, actual in zip(expected_npth, npth, strict=True):
                for a, b in zip(expected, actual, strict=True):
                    self.assertLess(abs(a - b), 1e-6)
            measured = []
            for row in source["usb_clearances"]:
                contact = next(
                    i
                    for i, r in enumerate(source["all_contact_rectangles"])
                    if r["endpoint"] == row["endpoint"]
                )
                bounds = top[f"contacts{contact}"].bounds
                expected_bounds = row["bounds_mm"]
                # Also prove exact nominal rectangle bounds to 1 nm; the
                # 1 um shape observer tolerance is not a manufacturing margin.
                self.assertLess(
                    max(abs(a - b) for a, b in zip(bounds, expected_bounds, strict=True)), 1e-6
                )
                value = min(gap(bounds, h[1:], h[0] / 2) for h in npth)
                self.assertLess(abs(value - row["analytic_gap_mm"]), 1e-6)
                measured.append(
                    {
                        "endpoint": row["endpoint"],
                        "source_gap_mm": row["analytic_gap_mm"],
                        "gerber_drill_gap_mm": value,
                        "delta_mm": value - row["analytic_gap_mm"],
                    }
                )
            # Closed rectangular profile in actual Gerber coordinates.
            edge = next(p for p in files if p.suffix == ".gm1").read_text()
            coords = [
                local(int(x) / 1e6, int(y) / 1e6)
                for x, y in re.findall(r"X(-?\d+)Y(-?\d+)D0[12]\*", edge)
            ]
            self.assertEqual(len(coords), 8)
            # local() centers on the connector; board center is 5 mm above it.
            self.assertEqual(set(coords), {(-20, -7.5), (-20, 17.5), (20, -7.5), (20, 17.5)})
            segments = [(coords[i], coords[i + 1]) for i in range(0, 8, 2)]
            self.assertEqual(
                Counter(v for s in segments for v in s), Counter({v: 2 for v in set(coords)})
            )
            self.assertAlmostEqual(sum(math.dist(*s) for s in segments), 130)
            silk = next(p for p in files if p.suffix == ".gto").read_text()
            silk_y = [int(y) / 1e6 + 108 for y in re.findall(r"X-?\d+Y(-?\d+)D0[12]\*", silk)]
            self.assertTrue(silk_y)
            self.assertGreater(min(silk_y), 2)
            drc = json.loads((cam / "drc.json").read_text())
            counts = Counter(v["type"] for v in drc["violations"])
            self.assertEqual(counts, Counter({"hole_clearance": 4, "lib_footprint_issues": 1}))
            self.assertEqual(drc["unconnected_items"], [])
            hole_pads = {
                re.search(r"Pad (contacts\d+)", v["items"][0]["description"])[1]
                for v in drc["violations"]
                if v["type"] == "hole_clearance"
            }
            self.assertEqual(hole_pads, {"contacts0", "contacts1", "contacts10", "contacts11"})
            job = json.loads(next((cam / "gerber").glob("*.gbrjob")).read_text())
            self.assertEqual(job["GeneralSpecs"]["LayerNumber"], 2)
            self.assertEqual(job["GeneralSpecs"]["BoardThickness"], 1.6)
            self.assertEqual(float(node(nodes(pcb, "general")[0], "thickness")[0]), 1.6)
            stack = nodes(nodes(nodes(pcb, "setup")[0], "stackup")[0], "layer")
            self.assertAlmostEqual(sum(float(node(l, "thickness")[0]) for l in stack), 1.2)
            functions = {
                p.name: re.search(r"%TF.FileFunction,([^*]+)\*%", p.read_text())[1]
                for p in files[:9]
            }
            self.assertEqual(
                set(functions.values()),
                {
                    "Copper,L1,Top",
                    "Copper,L2,Bot",
                    "Soldermask,Top",
                    "Soldermask,Bot",
                    "Paste,Top",
                    "Paste,Bot",
                    "Legend,Top",
                    "Legend,Bot",
                    "Profile,NP",
                },
            )
            results.append(
                {
                    "run": index,
                    "pcb_pad_comparison": pcb_distances,
                    "gerber_pad_comparison": comparisons,
                    "clearances": measured,
                    "npth_hits_local_mm": npth,
                    "pth_slots_local_mm": pth,
                    "gerber_functions": functions,
                    "drc_counts": dict(counts),
                    "unconnected_count": 0,
                    "routes_vias_zones": 0,
                    "silkscreen_minimum_board_y_mm": min(silk_y),
                    "outline_mm": [40, 25],
                    "general_and_job_thickness_mm": 1.6,
                    "source_and_exported_stackup_total_mm": 1.2,
                }
            )
            fabrication.append(files)
        self.assertEqual(boards[0], boards[1])
        differences = []
        for first, second in zip(*fabrication, strict=True):
            self.assertEqual(first.name, second.name)
            a, b = first.read_bytes(), second.read_bytes()
            self.assertEqual(
                without_times("cam/" + first.name, a.decode()),
                without_times("cam/" + second.name, b.decode()),
            )
            differences.append(
                {
                    "file": first.name,
                    "byte_identical": a == b,
                    "classification": "identical" if a == b else "verified timestamps only",
                }
            )
        write(
            "reconciliation.json",
            {
                "result": "PASS qualification fidelity only",
                "runs": results,
                "observer_tolerance_mm": tolerance,
                "relevant_bounds_and_gaps_tolerance_mm": 1e-6,
                "two_run_fabrication_comparison": differences,
                "pcb_semantics_equal": True,
                "external_dfm_result": None,
                "manufacturing_disposition": "UNRESOLVED",
            },
        )
        # Fixed ZIP entry timestamps make packaging reproducible for exact input
        # bytes; fabrication files themselves are copied without any alteration.
        with ZipFile(ZIP_PATH, "w", compression=ZIP_STORED) as archive:
            for path in fabrication[0]:
                info = ZipInfo(path.name, date_time=(2026, 10, 4, 0, 0, 0))
                archive.writestr(info, path.read_bytes())
        with ZipFile(ZIP_PATH) as archive:
            self.assertEqual(archive.namelist(), [p.name for p in fabrication[0]])
            for p in fabrication[0]:
                self.assertEqual(archive.read(p.name), p.read_bytes())
            self.assertFalse(
                any(
                    n.endswith((".gbrjob", ".kicad_pcb", ".kicad_sch", ".kicad_pro"))
                    for n in archive.namelist()
                )
            )
        pipeline = json.loads((EVIDENCE / "pipeline.json").read_text())
        write(
            "upload-manifest.json",
            {
                "source_commit": pipeline["source_commit"],
                "baseline": pipeline["baseline"],
                "qualification_only": True,
                "status": "HUMAN DFM UPLOAD ONLY - DO NOT ORDER",
                "zip_path": str(ZIP_PATH),
                "zip_sha256": digest(ZIP_PATH.read_bytes()),
                "zip_bytes": ZIP_PATH.stat().st_size,
                "selected_run": 1,
                "files": {
                    p.name: {"bytes": p.stat().st_size, "sha256": digest(p.read_bytes())}
                    for p in fabrication[0]
                },
                "unchanged_bytes_verified": True,
                "geometry_postprocessing": False,
                "cad_and_job_excluded": True,
                "external_dfm_result": None,
                "production_acceptable": None,
                "analysis_source_sha256": {
                    str(path.relative_to(PROJECT)): digest(path.read_bytes())
                    for path in [PROJECT / "physical/qualify_c4b4a.py"]
                },
            },
        )
        protected()


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(Reconcile)
    )
    raise SystemExit(0 if result.wasSuccessful() else 1)
