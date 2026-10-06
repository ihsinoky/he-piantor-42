"""Read-only two-process material comparison; never repairs generated data.

Circuit JSON: canonical physical categories, resolved component/port names,
source requirements, and independent connectivity summaries. IDs and record
order are removed. Exact numeric geometry is retained (no rounding).
Manufacturing: compare every copper/drill instruction after removing ONLY
the pinned exporter's creation-date metadata/comments. ZIP ordering/times are
ignored by addressing members by name. Apertures and coordinates are retained.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys
import zipfile

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))

def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()

def ordered(values):
    return sorted(values, key=canonical)

def physical(j):
    names = {e["source_component_id"]: e["name"] for e in j if e["type"] == "source_component"}
    pcb_names = {e["pcb_component_id"]: names[e["source_component_id"]] for e in j if e["type"] == "pcb_component"}
    ports = {e["source_port_id"]: names[e["source_component_id"]]+"."+e["name"] for e in j if e["type"] == "source_port"}
    nets = {e["source_net_id"]: e["name"] for e in j if e["type"] == "source_net"}
    pcb_ports = {e["pcb_port_id"]: ports[e["source_port_id"]] for e in j if e["type"] == "pcb_port"}

    def clean(e):
        result = {k: v for k, v in e.items() if not k.endswith(("_id", "_ids")) and k != "subcircuit_connectivity_map_key"}
        if "source_component_id" in e:
            result["component_name"] = names[e["source_component_id"]]
        if "pcb_component_id" in e:
            result["component_name"] = pcb_names[e["pcb_component_id"]]
        if "pcb_port_id" in e:
            result["port_name"] = pcb_ports[e["pcb_port_id"]]
        for k in ["layers", "port_hints"]:
            if k in result:
                result[k] = sorted(result[k])
        return result

    categories = {}
    types = {"board": ["pcb_board"], "placement": ["pcb_component"],
             "pads": ["pcb_smtpad", "pcb_plated_hole"], "vias": ["pcb_via"],
             "mechanical_and_keepout": ["pcb_hole", "pcb_cutout", "pcb_keepout", "pcb_courtyard"]}
    for category, selected in types.items():
        categories[category] = ordered([clean(e) for e in j if e["type"] in selected])
    routes = []
    for t in (e for e in j if e["type"] == "pcb_trace"):
        segments = []
        for a, b in zip(t["route"], t["route"][1:]):
            layer = b.get("layer") if a["route_type"] == "via" else a.get("layer")
            segments.append({"ends": sorted([[a["x"], a["y"]], [b["x"], b["y"]]]),
                             "layer": layer, "width": a.get("width", b.get("width"))})
        routes.append(ordered(segments))
    categories["routes"] = ordered(routes)
    requirements = []
    for e in j:
        if e["type"] == "source_trace":
            requirements.append({"ports": sorted(ports[p] for p in e.get("connected_source_port_ids", [])),
                                 "nets": sorted(nets[n] for n in e.get("connected_source_net_ids", []))})
        elif e["type"] == "source_component_internal_connection":
            requirements.append({"internal_ports": sorted(ports[p] for p in e["source_port_ids"])})
        elif e["type"] == "source_port":
            requirements.append({"port": ports[e["source_port_id"]], "nc": e.get("do_not_connect", False)})
    categories["source_requirements"] = ordered(requirements)
    return categories

def normalize_file(name, raw):
    lines = raw.decode().splitlines()
    if name.endswith(".gbr"):
        lines = [l for l in lines if not l.startswith("%TF.CreationDate,") and not (l.startswith("G04 Created by tscircuit (builder) date "))]
    elif name.endswith(".drl"):
        lines = [l for l in lines if not l.startswith(("; DRILL file {tscircuit} date ", "; #@! TF.CreationDate,"))]
    return "\n".join(lines)

def run(directory):
    p = Path(directory)
    raw = (p/"circuit.json").read_bytes()
    categories = physical(json.loads(raw))
    summary = json.loads((p/"summary.json").read_text())
    assert summary["raw_sha256"] == hashlib.sha256(raw).hexdigest(), "Physical summary is stale"
    categories["connectivity"] = {k: summary[k] for k in ["source_net_count", "required_physical_endpoint_count",
        "routed_trace_count", "via_count", "electrically_required_unrouted_count", "intentional_nc_count",
        "wrong_net_copper_components", "unsupported_geometry", "invalid_layer_transitions", "unassigned_non_nc_ports"]}
    categories["connectivity"]["net_results"] = ordered([{k: e[k] for k in ["nets", "required_endpoints", "copper_islands", "missing_physical_ports", "unrouted_connections"]} for e in summary["net_results"]])
    generation = json.loads((p/"generation.json").read_text())
    z = zipfile.ZipFile(p/"manufacturing.zip")
    files = ["F_Cu.gbr", "B_Cu.gbr", "Edge_Cuts.gbr", "drill-L1-L2.drl", "drill_npth.drl", "bom.csv", "pick_and_place.csv"]
    manufacturing = {f: normalize_file(f, z.read(f)) for f in files}
    return {"raw_circuit_sha256": hashlib.sha256(raw).hexdigest(), "source_sha256": generation["source_sha256"],
            "normalized_material_sha256": digest(categories), "category_sha256": {k: digest(v) for k, v in categories.items()},
            "raw_manufacturing_sha256": {f: hashlib.sha256(z.read(f)).hexdigest() for f in files},
            "normalized_manufacturing_sha256": {f: digest(t) for f, t in manufacturing.items()}}

def self_check(j):
    # Metamorphic checks distinguish harmless ID/order changes from movement,
    # lost vias, wrong source intent and timestamp-only export differences.
    original = digest(physical(j))
    ids = {v for e in j for k, v in e.items() if k.endswith("_id") and isinstance(v, str)}
    rename = lambda value: "renamed_"+value if value in ids else value
    def transformed(value):
        if isinstance(value, str):
            return rename(value)
        if isinstance(value, list):
            return [transformed(x) for x in value]
        if isinstance(value, dict):
            return {k: transformed(v) for k, v in value.items()}
        return value
    assert digest(physical(list(reversed(transformed(j))))) == original
    moved = copy.deepcopy(j)
    next(e for e in moved if e["type"] == "pcb_smtpad")["x"] += .01
    assert digest(physical(moved)) != original
    assert digest(physical([e for e in j if e["type"] != "pcb_via"])) != original
    changed = copy.deepcopy(j)
    next(e for e in changed if e["type"] == "source_port")["do_not_connect"] = True
    assert digest(physical(changed)) != original
    assert normalize_file("F_Cu.gbr", b"%TF.CreationDate,one*%\nX1Y2D01*\n") == normalize_file("F_Cu.gbr", b"%TF.CreationDate,two*%\nX1Y2D01*\n")
    assert normalize_file("F_Cu.gbr", b"X1Y2D01*\n") != normalize_file("F_Cu.gbr", b"X2Y2D01*\n")
    return 6

if __name__ == "__main__":
    a, b, output = sys.argv[1:]
    checks = self_check(json.loads((Path(a)/"circuit.json").read_text()))
    first, second = run(a), run(b)
    assert first["source_sha256"] == second["source_sha256"], "Source content differs between runs"
    categories = [k for k in first["category_sha256"] if first["category_sha256"][k] != second["category_sha256"][k]]
    files = [f for f in first["normalized_manufacturing_sha256"] if first["normalized_manufacturing_sha256"][f] != second["normalized_manufacturing_sha256"][f]]
    result = {"result": "PASS" if not categories and not files else "MATERIAL_DIFFERENCE", "run_1": first, "run_2": second,
              "different_categories": categories, "different_manufacturing_files": files, "normalization_fault_checks": checks,
              "limitation": "Reproducibility does not waive either run's physical validation failures"}
    Path(output).write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ["run_1", "run_2"]}))
    sys.exit(0 if result["result"] == "PASS" else 1)
