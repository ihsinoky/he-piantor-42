"""Read-only deterministic verifier for the pinned stock Gerber archive.

Supports the emitted absolute metric 4.6 linear Gerbers and decimal Excellon.
Checks every route segment, every via on both copper layers and in drill,
the rectangular outline, GH lands, and all BOM/PnP component rows.
No archive or generated Circuit JSON is edited.
"""
import csv
import hashlib
import io
import json
import re
import sys
import zipfile

source, archive, output = sys.argv[1:]
j = json.load(open(source))
z = zipfile.ZipFile(archive)
required = ["F_Cu.gbr", "B_Cu.gbr", "Edge_Cuts.gbr", "drill-L1-L2.drl", "bom.csv", "pick_and_place.csv"]
data = {f: z.read(f).decode() for f in required}
assert all(data.values())

def point(x, y):
    return (round(float(x), 6), round(float(y), 6))

def segment(a, b):
    return tuple(sorted([a, b]))

def gerber(text):
    assert "%FSLAX46Y46*%" in text and "%MOMM*%" in text
    apertures = {int(n): (kind, tuple(float(x) for x in dimensions.split("X")))
                 for n, kind, dimensions in re.findall(r"%ADD(\d+)([CR]),([\d.X]+)\*%", text)}
    current, previous = None, None
    draws, flashes = set(), set()
    for line in text.splitlines():
        selected = re.fullmatch(r"D(\d+)\*", line)
        if selected:
            current = int(selected[1])
        command = re.fullmatch(r"X(-?\d+)Y(-?\d+)D0([123])\*", line)
        if not command:
            continue
        p = point(int(command[1])/1e6, int(command[2])/1e6)
        if command[3] == "1":
            assert previous is not None
            draws.add((segment(previous, p), apertures.get(current)))
        if command[3] == "3":
            flashes.add((p, apertures.get(current)))
        previous = p
    return draws, flashes

copper = {layer: gerber(data[file]) for layer, file in [("top", "F_Cu.gbr"), ("bottom", "B_Cu.gbr")]}
segments_checked = 0
for trace in (e for e in j if e["type"] == "pcb_trace"):
    route = trace["route"]
    for a, b in zip(route, route[1:]):
        pa, pb = point(a["x"], a["y"]), point(b["x"], b["y"])
        if pa == pb:
            continue
        layer = b.get("layer") if a["route_type"] == "via" else a["layer"]
        width = round(a.get("width", b.get("width")), 6)
        assert (segment(pa, pb), ("C", (width,))) in copper[layer][0], f"Missing routed segment: {trace['pcb_trace_id']} {pa} {pb} {layer} {width}"
        segments_checked += 1

tools = {n: float(d) for n, d in re.findall(r"^T(\d+)C([\d.]+)$", data["drill-L1-L2.drl"], re.M)}
drills, slots, tool, last_hit = set(), set(), None, None
for line in data["drill-L1-L2.drl"].splitlines():
    selected = re.fullmatch(r"T(\d+)", line)
    if selected:
        tool = selected[1]
    hit = re.fullmatch(r"X(-?[\d.]+)Y(-?[\d.]+)", line)
    if hit:
        last_hit = (round(float(hit[1]), 4), round(float(hit[2]), 4))
        drills.add((*last_hit, tools[tool]))
    slot = re.fullmatch(r"G85X(-?[\d.]+)Y(-?[\d.]+)", line)
    if slot:
        end = (round(float(slot[1]), 4), round(float(slot[2]), 4))
        slots.add((segment(last_hit, end), tools[tool]))
vias = [e for e in j if e["type"] == "pcb_via"]
for v in vias:
    for layer in ["top", "bottom"]:
        assert (point(v["x"], v["y"]), ("C", (v["outer_diameter"],))) in copper[layer][1]
    assert (round(v["x"], 4), round(v["y"], 4), v["hole_diameter"]) in drills

def region_boxes(text):
    boxes = set()
    for region in re.findall(r"G36\*(.*?)G37\*", text, re.S):
        vertices = [(int(x)/1e6, int(y)/1e6) for x, y in re.findall(r"X(-?\d+)Y(-?\d+)D0[12]\*", region)]
        assert vertices
        boxes.add(tuple(round(v, 6) for v in (min(p[0] for p in vertices), min(p[1] for p in vertices), max(p[0] for p in vertices), max(p[1] for p in vertices))))
    return boxes

plated = [e for e in j if e["type"] == "pcb_plated_hole"]
region_bounds = {l: region_boxes(data[f]) for l, f in [("top", "F_Cu.gbr"), ("bottom", "B_Cu.gbr")]}
for p in plated:
    if p["shape"] == "circle":
        for layer in p["layers"]:
            assert (point(p["x"], p["y"]), ("C", (p["outer_diameter"],))) in copper[layer][1]
        assert (round(p["x"], 4), round(p["y"], 4), p["hole_diameter"]) in drills
    else:
        assert p["shape"] == "oval" and p.get("ccw_rotation", 0) == 0, "Unsupported plated export geometry"
        bounds = tuple(round(v, 6) for v in (p["x"]-p["outer_width"]/2, p["y"]-p["outer_height"]/2, p["x"]+p["outer_width"]/2, p["y"]+p["outer_height"]/2))
        for layer in p["layers"]:
            assert bounds in region_bounds[layer], "Plated slot copper envelope missing"
        dx, dy = max(0, p["hole_width"]-p["hole_height"])/2, max(0, p["hole_height"]-p["hole_width"])/2
        ends = segment((round(p["x"]-dx, 4), round(p["y"]-dy, 4)), (round(p["x"]+dx, 4), round(p["y"]+dy, 4)))
        assert (ends, min(p["hole_width"], p["hole_height"])) in slots

board = next(e for e in j if e["type"] == "pcb_board")
w, h = board["width"]/2, board["height"]/2
corners = [(-w, -h), (w, -h), (w, h), (-w, h)]
outline = {s for s, _ in gerber(data["Edge_Cuts.gbr"])[0]}
assert all(segment(a, b) in outline for a, b in zip(corners, corners[1:] + corners[:1]))
connector = next(e for e in j if e["type"] == "source_component" and e["name"] == "J_WING")
pcb = next(e for e in j if e["type"] == "pcb_component" and e["source_component_id"] == connector["source_component_id"])
pads = [e for e in j if e["type"] == "pcb_smtpad" and e["pcb_component_id"] == pcb["pcb_component_id"]]
assert len(pads) == 16
assert all((point(p["x"], p["y"]), ("R", (p["width"], p["height"]))) in copper["top"][1] for p in pads)
smt_pads = [e for e in j if e["type"] == "pcb_smtpad"]
for p in smt_pads:
    if p["shape"] == "circle":
        aperture = ("C", (2*p["radius"],))
    else:
        assert p["shape"] == "rect", "Unsupported SMT export geometry"
        angle = p.get("ccw_rotation", 0) % 180
        assert angle in (0, 90), "Unsupported rectangle rotation"
        dimensions = (p["width"], p["height"]) if angle == 0 else (p["height"], p["width"])
        aperture = ("R", tuple(round(d, 6) for d in dimensions))
    assert (point(p["x"], p["y"]), aperture) in copper[p["layer"]][1], f"Missing SMT copper {p['pcb_smtpad_id']}"
components = [e for e in j if e["type"] == "source_component"]
# Source-authored bare copper test pads need no assembly part. The pinned
# exporter omits these from BOM/PnP; verify their actual copper instead.
bare_pads = [e for e in components if e.get("ftype") == "simple_test_point" and e.get("footprint_variant") == "pad"]
for c in bare_pads:
    pcomp = next(e for e in j if e["type"] == "pcb_component" and e["source_component_id"] == c["source_component_id"])
    ps = [e for e in j if e["type"] == "pcb_smtpad" and e["pcb_component_id"] == pcomp["pcb_component_id"]]
    assert ps and all((point(p["x"], p["y"]), ("C", (2*p["radius"],))) in copper[p["layer"]][1] for p in ps)
refs = {e["name"] for e in components if e not in bare_pads}
assert refs <= {r["Designator"] for r in csv.DictReader(io.StringIO(data["bom.csv"]))}
assert refs <= {r["Designator"] for r in csv.DictReader(io.StringIO(data["pick_and_place.csv"]))}
result = {"result": "PASS", "purpose": "diagnostic export geometry only; physical DRC still FAIL",
          "route_segments_checked": segments_checked, "via_count_checked": len(vias), "connector_lands_checked": len(pads),
          "all_smt_pads_checked": len(smt_pads),
          "all_plated_lands_checked": len(plated),
          "all_component_rows_present": True, "required_routed_net_disappeared": False,
          "bare_copper_test_pads_checked": [e["name"] for e in bare_pads],
          "net_survival_method": "every physical route segment survives on its original layer with its width; Gerber has no net names",
          "raw_file_sha256": {f: hashlib.sha256(z.read(f)).hexdigest() for f in required},
          "limitations": ["supplier PnP rotations unverified", "BOM supplier identities incomplete; not procurement data"]}
open(output, "w").write(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: v for k, v in result.items() if k != "raw_file_sha256"}))
