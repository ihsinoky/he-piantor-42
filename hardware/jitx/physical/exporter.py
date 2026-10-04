"""Public export-plugin qualification observer; never edits generated geometry.

BOM/PnP CSVs are review artifacts, not an orderable JLCPCB assembly package.
Coordinates use the JITX board frame (mm, Y up); angles are CCW from each
accepted landpattern's local X axis. Supplier rotation conventions are unproven.
"""

import csv
import json
from pathlib import Path
from typing import Any

from jitx.circuit import Route
from jitx.component import Component
from jitx.inspect import visit
from jitx.landpattern import Landpattern, Pad, PadShape
from jitx.placement import Placement
from jitx.plugin.export import Export
from jitx.run import RuntimeDesign
from jitx.via import Via

from parity.exporter import M1ElectricalGraphExport


@Export.register("physical-qualification")
class PhysicalQualificationExport(M1ElectricalGraphExport):
    """Capture source-controlled placement and copper through public APIs."""

    def submitted(self, design: RuntimeDesign, /, *args: Any, **kwargs: Any) -> None:
        super().submitted(design, *args, **kwargs)
        self.source_poses = {}
        for trace, component in design.query(Component):
            if trace.transform is None or component.transform is None:
                raise ValueError(f"Source has floating component: {trace.path}")
            self.source_poses[str(trace.path)] = (trace.transform * component.transform).trs

    def export(self, design: RuntimeDesign, /, output: Path = Path("designs/c4b")) -> None:
        output.mkdir(parents=True, exist_ok=True)
        records = {row["identity"]: row for row in self.graph["components"]}
        placements = []
        pad_shapes = []
        for trace, component in design.query(Component):
            if trace.transform is None or component.transform is None:
                raise ValueError(f"Missing transform: {trace.path}")
            pose = trace.transform * component.transform
            if pose.trs != self.source_poses[str(trace.path)]:
                raise ValueError(f"Runtime changed source placement: {trace.path}")
            if not isinstance(pose, Placement) or not component.reference_designator:
                raise ValueError(f"Missing captured placement/refdes: {trace.path}")
            landpatterns = list(visit(component, Landpattern))
            placements.append(
                {
                    "identity": str(trace.path),
                    "refdes": component.reference_designator,
                    "x_mm": pose.translation[0],
                    "y_mm": pose.translation[1],
                    "rotation_ccw_deg": pose.rotation,
                    "side": pose.side.name,
                    "mpn": component.mpn,
                    "manufacturer": component.manufacturer,
                    "value": records[str(trace.path)]["value"],
                    "supplier_part_number": records[str(trace.path)]["supplier_part_number"],
                    "footprints": [type(lp).__name__ for _, lp in landpatterns],
                }
            )
            # Public physical pads transformed into the board frame: observer only.
            for pad_trace, pad in visit(component, Pad):
                if pad_trace.transform is None or pad.transform is None:
                    raise ValueError("Unplaced pad")
                pad_shape = pad.shape.shape if isinstance(pad.shape, PadShape) else pad.shape
                shape = (pose * pad_trace.transform * pad.transform) * pad_shape
                pad_shapes.append((str(trace.path), shape.to_shapely()))
        placements.sort(key=lambda row: row["identity"])
        routes = []
        for trace, route in design.query(Route):
            shapes = [
                shape.to_shapely().wkt for copper in route.traces or () for shape in copper.shapes
            ]
            routes.append(
                {
                    "identity": str(trace.path),
                    "layer": route.layer,
                    "realized": bool(shapes),
                    "copper_wkt_mm": shapes,
                }
            )
        # This is a narrow independent placement check, never a full DRC claim.
        overlaps = [
            [left_name, right_name]
            for i, (left_name, left) in enumerate(pad_shapes)
            for right_name, right in pad_shapes[i + 1 :]
            if left_name != right_name and left.intersection(right).area > 1e-9
        ]
        report = {
            "schema_version": 1,
            "design": design.name,
            "qualification_only": True,
            "placements": placements,
            "routes": routes,
            "vias": [str(trace.path) for trace, _ in design.query(Via)],
            "inter_component_pad_overlaps": sorted({tuple(pair) for pair in overlaps}),
            "source_poses_preserved": True,
            "pads_outside_board": sorted(
                {
                    name
                    for name, shape in pad_shapes
                    if not design.root.board.shape.to_shapely().covers(shape)
                }
            ),
            "full_board_routing_complete": False,
            "full_drc_pass": False,
            "coordinate_convention": "JITX frame; mm; Y up; CCW; local footprint origin",
        }
        (output / "physical-observation.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n"
        )
        (output / "electrical-graph.json").write_text(
            json.dumps(self.graph, indent=2, sort_keys=True) + "\n"
        )
        with (output / "bom-review.csv").open("w", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["Designator", "Comment", "Footprint", "Manufacturer", "MPN", "LCSC"])
            for row in placements:
                writer.writerow(
                    [
                        row["refdes"],
                        row["value"],
                        ";".join(row["footprints"]),
                        row["manufacturer"],
                        row["mpn"],
                        row["supplier_part_number"],
                    ]
                )
        with (output / "pnp-review.csv").open("w", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["Designator", "Mid X (mm)", "Mid Y (mm)", "Layer", "Rotation"])
            for row in placements:
                writer.writerow(
                    [row["refdes"], row["x_mm"], row["y_mm"], row["side"], row["rotation_ccw_deg"]]
                )
