"""Read-only reconciliation of C4B2 outputs, using the public JITX test harness.

S-expression parsing observes the downstream interchange, never changes it.
Every raw hash is retained; semantic comparison removes only specified IDs,
net-number aliases and record ordering, leaving every other PCB field intact.
"""

import csv
import json
import math
import re
import unittest
from collections import Counter

from jitx.component import Component
from jitx.inspect import visit
from jitx.landpattern import Pad, PadMapping, PadShape
from jitx.net import Port
from jitx.shapes.primitive import Circle
from jitx.substrate import SubstrateContext
from jitx.test import TestCase
from jitxlib.landpatterns.pads import NPTHPad
from shapely import affinity, wkt
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

from he_piantor_42_jitx.physical_qualification import (
    M1PhysicalQualificationCircuit,
    QualificationSubstrate,
)
from parity.m1 import evaluate, load_inputs
from physical.reproduce_c4b2 import DESIGN, EVIDENCE, OUTPUT, PROJECT, digest


def nodes(node: list, key: str) -> list:
    return [x for x in node if isinstance(x, list) and x and x[0] == key]


def node(node_: list, key: str, default=None):
    matches = nodes(node_, key)
    return matches[0][1:] if matches else default


def parse(text: str) -> list:
    stack = [[]]
    for token in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text):
        if token == "(":
            stack.append([])
        elif token == ")":
            stack[-2].append(stack.pop())
        else:
            stack[-1].append(json.loads(token) if token.startswith('"') else token)
    if len(stack) != 1 or len(stack[0]) != 1:
        raise ValueError("Malformed S-expression")
    return stack[0][0]


def xy(values: list) -> tuple:
    return tuple(map(float, values[:2]))


def jitx_frame(shape):
    return affinity.affine_transform(shape, [1, 0, 0, -1, -139.5, 108])


def pose(shape, at: list):
    # KiCad positive angles rotate CCW on the physical board, with screen Y down.
    angle = float(at[2]) if len(at) > 2 else 0
    return affinity.translate(affinity.rotate(shape, -angle, origin=(0, 0)), *xy(at))


def pad_geometry(pad: list, footprint: list):
    size = xy(node(pad, "size"))
    if pad[3] == "custom":
        primitives = nodes(pad, "primitives")[0]
        shapes = [
            Polygon([xy(p[1:]) for p in nodes(nodes(poly, "pts")[0], "xy")])
            for poly in nodes(primitives, "gr_poly")
        ]
        shape = unary_union(shapes)
    elif pad[3] == "circle":
        shape = Point(0, 0).buffer(size[0] / 2, quad_segs=64)
    elif pad[3] == "oval":
        radius = min(size) / 2
        span = abs(size[0] - size[1]) / 2
        ends = [(-span, 0), (span, 0)] if size[0] > size[1] else [(0, -span), (0, span)]
        shape = LineString(ends).buffer(radius, quad_segs=64)
    elif pad[3] == "rect":
        x, y = size[0] / 2, size[1] / 2
        shape = Polygon([(-x, -y), (x, -y), (x, y), (-x, y)])
    else:
        raise ValueError(f"Unqualified pad shape {pad[3]}")
    # Exported pad rotation is absolute; remove footprint angle before composing.
    at = node(pad, "at", ["0", "0", "0"])
    fp_at = node(footprint, "at")
    relative = [*at[:2], str(float(at[2] if len(at) > 2 else 0) - float(fp_at[2]))]
    return jitx_frame(pose(pose(shape, relative), fp_at))


def semantic_pcb(pcb: list):
    nets = {n[1]: n[2] for n in nodes(pcb, "net")}

    def normalized(value):
        if not isinstance(value, list):
            return value
        if value and value[0] in {"uuid", "tstamp"}:
            return None
        if value and value[0] == "net":
            return ["net", nets.get(value[1], "")]  # Numeric aliases, retain net name.
        if value[0] in {"pts", "layers", "stackup"}:
            return [normalized(v) for v in value]
        # Preserve ordered scalar coordinates and polygon vertex sequences.
        scalars = [v for v in value if not isinstance(v, list)]
        children = [normalized(v) for v in value if isinstance(v, list)]
        return scalars + sorted(
            (v for v in children if v is not None), key=lambda v: json.dumps(v, sort_keys=True)
        )

    return normalized(pcb)


def track_shape(track: list):
    start, end = xy(node(track, "start")), xy(node(track, "end"))
    points = [start, end]
    if track[0] == "arc":
        mid = xy(node(track, "mid"))
        a, b, c = start, mid, end
        det = 2 * (a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1]))
        q = [x * x + y * y for x, y in (a, b, c)]
        cx = (q[0] * (b[1] - c[1]) + q[1] * (c[1] - a[1]) + q[2] * (a[1] - b[1])) / det
        cy = (q[0] * (c[0] - b[0]) + q[1] * (a[0] - c[0]) + q[2] * (b[0] - a[0])) / det
        angles = [math.atan2(y - cy, x - cx) for x, y in (a, b, c)]
        sweep = (angles[2] - angles[0]) % (2 * math.pi)
        if (angles[1] - angles[0]) % (2 * math.pi) > sweep:
            sweep -= 2 * math.pi
        radius = math.dist(a, (cx, cy))
        points = [
            (
                cx + radius * math.cos(angles[0] + sweep * i / 128),
                cy + radius * math.sin(angles[0] + sweep * i / 128),
            )
            for i in range(129)
        ]
    return jitx_frame(LineString(points).buffer(float(node(track, "width")[0]) / 2, quad_segs=64))


class Reconcile(TestCase):
    """Actual source instantiation in JITX's documented TestCase context."""

    def test_downstream_fidelity(self):
        historical = json.loads((PROJECT / "physical/evidence/build-manifest.json").read_text())
        validation = json.loads((PROJECT / "physical/evidence/validation.json").read_text())
        source = {}
        with SubstrateContext(QualificationSubstrate()):
            circuit = M1PhysicalQualificationCircuit()
            for trace, component in visit(circuit, Component):
                ports = {id(p): f"circuit.{trace.path}.{t.path}" for t, p in visit(component, Port)}
                memberships = {}
                for _, mapping in visit(component, PadMapping):
                    for port, pads in mapping.items():
                        for pad in [pads] if isinstance(pads, Pad) else pads:
                            memberships[id(pad)] = ports[id(port)]
                if not memberships:
                    # Documented Component default: ports map to pads in order.
                    memberships = {
                        id(pad): ports[id(port)]
                        for (_, port), (_, pad) in zip(
                            visit(component, Port), visit(component, Pad), strict=True
                        )
                    }
                rows = []
                for pad_trace, pad in visit(component, Pad):
                    shape = pad.shape.shape if isinstance(pad.shape, PadShape) else pad.shape
                    geometry = (component.transform * pad_trace.transform * pad.transform) * shape
                    g = wkt.loads(geometry.to_shapely().wkt)
                    if isinstance(shape, Circle):
                        # Compare the analytic radius, not JITX's coarse display tessellation.
                        g = Point(*geometry.transform.translation).buffer(
                            shape.radius, quad_segs=64
                        )
                    rows.append(
                        {
                            "path": str(pad_trace.path),
                            "geometry": g,
                            "endpoint": memberships.get(id(pad)),
                        }
                    )
                for hole_trace, hole in visit(component, NPTHPad):
                    geometry = (
                        component.transform * hole_trace.transform * hole.transform
                    ) * hole.cutout.shape
                    g = wkt.loads(geometry.to_shapely().wkt)
                    if isinstance(hole.cutout.shape, Circle):
                        g = Point(*geometry.transform.translation).buffer(
                            hole.cutout.shape.radius, quad_segs=64
                        )
                    rows.append(
                        {
                            "path": str(hole_trace.path),
                            "geometry": g,
                            "endpoint": None,
                        }
                    )
                source[f"circuit.{trace.path}"] = rows
        results = []
        boards = []
        for index in (1, 2):
            run = OUTPUT / f"run-{index}"
            observation = json.loads((run / "physical-observation.json").read_text())
            graph = json.loads((run / "electrical-graph.json").read_text())
            pcb = parse((run / "kicad" / f"{DESIGN}.kicad_pcb").read_text())
            boards.append(pcb)
            net_names = {n[1]: n[2] for n in nodes(pcb, "net")}
            footprints = {
                next(t[2] for t in nodes(fp, "fp_text") if t[1] == "reference"): fp
                for fp in nodes(pcb, "footprint")
            }
            self.assertEqual(len(footprints), 68)
            poses = {
                r["identity"]: {
                    k: r[k]
                    for k in ("identity", "refdes", "x_mm", "y_mm", "rotation_ccw_deg", "side")
                }
                for r in observation["placements"]
            }
            self.assertEqual(list(poses.values()), validation["placements"])
            groups = {endpoint: n for n in graph["nets"] for endpoint in n["members"]}
            unnamed_aliases = {}
            pad_diffs, placement_diffs, net_diffs = [], [], []
            pad_uuid = {}
            connected_counts = Counter()
            for row in observation["placements"]:
                fp = footprints[row["refdes"]]
                at = node(fp, "at")
                expected = [row["x_mm"] + 139.5, 108 - row["y_mm"], row["rotation_ccw_deg"]]
                if any(abs(float(a) - b) > 1e-6 for a, b in zip(at, expected, strict=True)):
                    placement_diffs.append(row["identity"])
                if node(fp, "layer") != ["F.Cu"]:
                    placement_diffs.append(row["identity"] + ":side")
                all_pads = nodes(fp, "pad")
                # Legacy export represents NPTH mask openings as separate SMD
                # records. They carry no copper/net and are not extra source pads.
                mask_only = [
                    p
                    for p in all_pads
                    if p[2] == "smd" and not any("Cu" in layer for layer in node(p, "layers"))
                ]
                for p in mask_only:
                    self.assertIsNone(node(p, "net"))
                    self.assertEqual(set(node(p, "layers")), {"F.Mask", "B.Mask"})
                pads = [p for p in all_pads if p not in mask_only]
                remaining = list(source[row["identity"]])
                for pad in pads:
                    geom = pad_geometry(pad, fp)
                    self.assertTrue(remaining, (row["identity"], pad[1], len(pads)))
                    closest = min(remaining, key=lambda r: r["geometry"].hausdorff_distance(geom))
                    distance = closest["geometry"].hausdorff_distance(geom)
                    if distance > 0.001:
                        pad_diffs.append(
                            {"refdes": row["refdes"], "pad": pad[1], "hausdorff_mm": distance}
                        )
                    remaining.remove(closest)
                    group = groups.get(closest["endpoint"])
                    actual = node(pad, "net", ["0", ""])[-1]
                    if group and group["name"]:
                        if group["name"] != actual:
                            net_diffs.append([closest["endpoint"], group["name"], actual])
                    elif group:
                        group_key = tuple(group["members"])
                        if not actual or unnamed_aliases.setdefault(group_key, actual) != actual:
                            net_diffs.append([closest["endpoint"], "unnamed direct link", actual])
                    elif actual:
                        net_diffs.append([closest["path"], "unconnected/NPTH", actual])
                    if actual:
                        connected_counts[actual] += 1
                    pad_uuid[node(pad, "tstamp")[0]] = {
                        "net": actual,
                        "refdes": row["refdes"],
                        "endpoint": closest["endpoint"],
                    }
                self.assertFalse(remaining)
            self.assertEqual(len(set(unnamed_aliases.values())), 4, (unnamed_aliases, net_diffs))
            self.assertFalse(pad_diffs, pad_diffs)
            self.assertFalse(placement_diffs, placement_diffs)
            self.assertFalse(net_diffs, net_diffs)
            vias = nodes(pcb, "via")
            via_facts = [
                {
                    "at": xy(node(v, "at")),
                    "size": float(node(v, "size")[0]),
                    "drill": float(node(v, "drill")[0]),
                    "layers": node(v, "layers"),
                    "net": net_names[node(v, "net")[0]],
                }
                for v in vias
            ]
            self.assertEqual(sorted(v["at"] for v in via_facts), [(170.5, 120.0), (172.5, 120.0)])
            self.assertTrue(
                all(
                    v["size"] == 0.65
                    and v["drill"] == 0.3
                    and v["net"] == "H0_RAW"
                    and v["layers"] == ["F.Cu", "B.Cu"]
                    for v in via_facts
                )
            )
            lines = nodes(pcb, "gr_line")
            outline = sorted(
                (xy(node(l, "start")), xy(node(l, "end")))
                for l in lines
                if node(l, "layer") == ["Edge.Cuts"]
            )
            self.assertEqual(
                outline,
                sorted(
                    [
                        ((179.5, 78), (99.5, 78)),
                        ((99.5, 78), (99.5, 138)),
                        ((99.5, 138), (179.5, 138)),
                        ((179.5, 138), (179.5, 78)),
                    ]
                ),
            )
            copper_layers = [l[1] for l in nodes(pcb, "layers")[0][1:] if l[2] == "signal"]
            self.assertEqual(copper_layers, ["F.Cu", "B.Cu"])
            tracks = nodes(pcb, "segment") + nodes(pcb, "arc")
            route_comparisons = []
            for layer in (0, 1):
                expected = unary_union(
                    [
                        wkt.loads(s)
                        for r in observation["routes"]
                        if r["layer"] == layer
                        for s in r["copper_wkt_mm"]
                    ]
                )
                actual = unary_union(
                    [
                        track_shape(t)
                        for t in tracks
                        if node(t, "layer") == [["F.Cu", "B.Cu"][layer]]
                    ]
                )
                distance = expected.hausdorff_distance(actual)
                route_comparisons.append(
                    {
                        "layer": layer,
                        "hausdorff_mm": distance,
                        "symmetric_difference_mm2": expected.symmetric_difference(actual).area,
                    }
                )
                # Existing C4B WKT uses documented ShapelyGeometry.from_shape
                # default arc-approximation tolerance 0.01 mm.
                self.assertLess(distance, 0.01)
            self.assertEqual(
                Counter(net_names[node(t, "net")[0]] for t in tracks),
                Counter({"H0_RAW": 5, "H1_RAW": 1, "H2_RAW": 1, "H3_RAW": 1}),
            )
            with (run / "cam/positions.csv").open() as f:
                positions = list(csv.DictReader(f))
            self.assertEqual(len(positions), 68)
            for p in positions:
                at = node(footprints[p["Ref"]], "at")
                self.assertAlmostEqual(float(p["PosX"]), float(at[0]), places=6)
                self.assertAlmostEqual(float(p["PosY"]), -float(at[1]), places=6)
                self.assertAlmostEqual(float(p["Rot"]), float(at[2]), places=6)
                self.assertEqual(p["Side"], "top")
            gerbers = sorted((run / "cam/gerber").glob("*"))
            self.assertEqual(
                {p.suffix for p in gerbers},
                {".gtl", ".gbl", ".gts", ".gbs", ".gtp", ".gbp", ".gto", ".gbo", ".gm1", ".gbrjob"},
            )
            job = json.loads(next(p for p in gerbers if p.suffix == ".gbrjob").read_text())
            self.assertEqual(job["GeneralSpecs"]["LayerNumber"], 2)
            for item in job["FilesAttributes"]:
                text = (run / "cam/gerber" / item["Path"]).read_text()
                self.assertIn("%MOMM*%", text)
                actual_function = re.search(r"%TF.FileFunction,([^*]+)\*%", text)[1]
                expected_function = (
                    item["FileFunction"]
                    .replace("SolderPaste", "Paste")
                    .replace("SolderMask", "Soldermask")
                )
                if expected_function == "Profile":
                    expected_function = "Profile,NP"
                self.assertEqual(actual_function, expected_function)
            drills = {}
            for path in (run / "cam/drill").glob("*.drl"):
                tool = None
                tools, hits = {}, []
                for line in path.read_text().splitlines():
                    if match := re.fullmatch(r"T(\d+)C([\d.]+)", line):
                        tools[match[1]] = float(match[2])
                    elif match := re.fullmatch(r"T(\d+)", line):
                        tool = match[1]
                    elif line.startswith("X"):
                        values = [float(x) for x in re.findall(r"[XY](-?[\d.]+)", line)]
                        hits.append([tools[tool], *values])
                drills["NPTH" if "-NPTH" in path.name else "PTH"] = sorted(hits)
            self.assertEqual(drills["NPTH"], [[0.6, 111.61, -132.5], [0.6, 117.39, -132.5]])
            self.assertEqual(
                drills["PTH"],
                sorted(
                    [
                        [0.3, 170.5, -120],
                        [0.3, 172.5, -120],
                        [0.6, 110.175, -132.55, 110.175, -131.45],
                        [0.6, 110.175, -136.58, 110.175, -135.78],
                        [0.6, 118.825, -132.55, 118.825, -131.45],
                        [0.6, 118.825, -136.58, 118.825, -135.78],
                    ]
                ),
            )
            for artifact in (
                "physical-observation.json",
                "pnp-review.csv",
                "electrical-graph.json",
            ):
                self.assertEqual(
                    digest((run / artifact).read_bytes()), historical["runs"][0]["files"][artifact]
                )
            drc = json.loads((run / "cam/drc.json").read_text())
            per_net = Counter()
            unexplained = []
            for violation in drc["unconnected_items"]:
                names = {
                    re.search(r"\[([^]]+)\]", item["description"])[1] for item in violation["items"]
                }
                if len(names) != 1:
                    unexplained.append(violation)
                else:
                    per_net.update(names)
            # Number of disconnected pad-islands minus one, corrected only for
            # the four already-realized Hall/probe paths and multi-pad SHIELD.
            expected_unconnected = {
                n: max(0, c - 1 - (1 if n.startswith("H") and n.endswith("_RAW") else 0))
                for n, c in connected_counts.items()
            }
            expected_unconnected = {n: c for n, c in expected_unconnected.items() if c}
            self.assertEqual(dict(per_net), expected_unconnected)
            self.assertFalse(unexplained)
            hole_findings = [v for v in drc["violations"] if v["type"] == "hole_clearance"]
            source_hole_distances = []
            usb = source["circuit.J_USB"]
            holes = [p for p in usb if p["path"].startswith("landpattern.locating")]
            for finding in hole_findings:
                pad = pad_uuid[finding["items"][0]["uuid"]]
                source_pad = next(p for p in usb if p["endpoint"] == pad["endpoint"])
                distance = min(source_pad["geometry"].distance(h["geometry"]) for h in holes)
                source_hole_distances.append(
                    {
                        "endpoint": pad["endpoint"],
                        "source_gap_mm": distance,
                        "kicad_description": finding["description"],
                    }
                )
            results.append(
                {
                    "run": index,
                    "component_count": 68,
                    "physical_pad_count": len(pad_uuid),
                    "placement_differences": placement_diffs,
                    "pad_geometry_differences": pad_diffs,
                    "net_differences": net_diffs,
                    "unnamed_net_aliases": [
                        {"endpoints": list(k), "kicad_net": v} for k, v in unnamed_aliases.items()
                    ],
                    "copper_layers": copper_layers,
                    "outline": outline,
                    "vias": via_facts,
                    "source_route_comparison": route_comparisons,
                    "drc_counts": dict(Counter(v["type"] for v in drc["violations"])),
                    "unconnected_count": len(drc["unconnected_items"]),
                    "unconnected_per_net": dict(per_net),
                    "expected_unconnected_per_net": expected_unconnected,
                    "unrouted_reconciliation": "PASS",
                    "source_hole_clearance": source_hole_distances,
                    "general_thickness_mm": float(node(nodes(pcb, "general")[0], "thickness")[0]),
                    "stackup_total_mm": sum(
                        float(node(l, "thickness")[0])
                        for l in nodes(nodes(nodes(pcb, "setup")[0], "stackup")[0], "layer")
                    ),
                    "position_rows": 68,
                    "drill_hits": drills,
                    "gerber_file_functions": job["FilesAttributes"],
                    "gerber_job_thickness_mm": job["GeneralSpecs"]["BoardThickness"],
                    "route_observation_arc_tolerance_mm": 0.01,
                    "historical_c4b_capture_hashes_match": True,
                }
            )
        raw = json.loads((OUTPUT / "c2-regression.json").read_text())
        _, parity = evaluate(raw, *load_inputs())
        self.assertEqual(parity["result"], "PASS")
        component_ports = {p["identity"] for c in raw["components"] for p in c["ports"]}

        def original_nets(g):
            return sorted(
                (n["name"] or "", sorted(set(n["members"]) & component_ports))
                for n in g["nets"]
                if set(n["members"]) & component_ports
            )

        self.assertEqual(raw["components"], graph["components"])
        self.assertEqual(original_nets(raw), original_nets(graph))
        self.assertEqual(
            original_nets(graph),
            sorted(
                (n["net"] or "", n["component_endpoints"])
                for n in historical["endpoint_routing_accounting"]
                if n["component_endpoints"]
            ),
        )
        self.assertEqual(semantic_pcb(boards[0]), semantic_pcb(boards[1]))
        summary = {
            "verdict": "BLOCKED",
            "runs": results,
            "electrical_parity": parity,
            "original_component_topology_preserved": True,
            "pcb_semantics_equal_excluding_ids_net_numbers_order": True,
            "blockers": [
                "Four source USB copper-to-NPTH gaps below 0.25 mm qualification rule",
                "KiCad general thickness 1.6 mm contradicts 1.2 mm source/exported stackup",
            ],
            "limitations": [
                "68 generated library-registration warnings",
                "Fixture partial routing remains independent of CAM",
                "Supplier rotation and assembly sourcing remain unqualified",
            ],
        }
        (EVIDENCE / "reconciliation.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(Reconcile)
    )
    raise SystemExit(0 if result.wasSuccessful() else 1)
