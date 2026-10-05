"""Fresh bounded C4B5 experiments through supported public export and DRC.

Generated KiCad input is mounted read-only. Historical evidence is never written.
Incomplete routing is recorded, never accepted on the basis of source requests.
"""

import importlib.metadata
import json
import os
import shutil
import subprocess
from collections import Counter

from parity.m1 import evaluate, load_inputs
from physical.reproduce import ELECTRICAL, PROJECT, digest
from physical.reproduce_c4b2 import IMAGE, inventory

EVIDENCE = PROJECT / "physical/c4b5-evidence"
OUTPUT = PROJECT / "designs/c4b5"
DESIGNS = [
    "he_piantor_42_jitx.routing_qualification.CompleteRoutingQualification",
    "he_piantor_42_jitx.routing_qualification.ViaRoutingQualification",
]


def write(name, value):
    (EVIDENCE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main():
    EVIDENCE.mkdir(exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    versions = {p: importlib.metadata.version(p) for p in ("jitx", "jitxlib-standard")}
    if versions != {"jitx": "4.4.3", "jitxlib-standard": "4.4.0"}:
        raise ValueError(versions)
    sources = {
        str(p.relative_to(PROJECT)): digest(p.read_bytes())
        for root in ("he_piantor_42_jitx", "physical", "parity")
        for p in sorted((PROJECT / root).rglob("*.py"))
    }
    commands = []
    pipeline = {"versions": versions, "source_sha256": sources, "commands": commands, "runs": []}

    def command(args, log, accepted=(0,)):
        result = subprocess.run(args, cwd=PROJECT, capture_output=True, timeout=300, check=False)
        log.write_bytes(result.stdout + result.stderr)
        commands.append(
            {
                "argv": args,
                "returncode": result.returncode,
                "log": str(log.relative_to(PROJECT)),
                "log_sha256": digest(log.read_bytes()),
            }
        )
        write("pipeline.json", pipeline)
        if result.returncode not in accepted:
            raise RuntimeError(f"Environment/command STOP: {args}; see {log}")
        return result.stdout.decode()

    runtime = json.loads(command(["jitx", "runtime", "introspect"], OUTPUT / "runtime.json"))
    versions["runtime"] = runtime["version"]
    versions["kicad"] = command(
        ["docker", "run", "--rm", IMAGE, "kicad-cli", "version"], OUTPUT / "kicad.log"
    ).strip()
    if versions["runtime"] != "4.4.2" or versions["kicad"] != "9.0.9":
        raise ValueError(versions)
    for index, design in enumerate(DESIGNS, 1):
        run = OUTPUT / f"experiment-{index}"
        if run.exists():
            shutil.rmtree(run)
        run.mkdir()
        command(["jitx", "runtime", "stop"], run / "stop.log")
        generated = PROJECT / "designs" / design
        if generated.exists():
            shutil.rmtree(generated)
        command(["jitx", "runtime", "start", "--background"], run / "start.log")
        command(["jitx", "design", "build", design, "--no-dependency-check"], run / "build.log")
        command(
            ["jitx", "design", "export", "physical-qualification", design, "--output", str(run)],
            run / "capture.log",
        )
        command(["jitx", "design", "export", "legacy-kicad", design], run / "export.log")
        shutil.copytree(generated / "kicad", run / "kicad")
        before = inventory(run / "kicad")
        (run / "cam").mkdir()
        command(
            [
                "docker",
                "run",
                "--rm",
                "--user",
                f"{os.getuid()}:{os.getgid()}",
                "-v",
                f"{run / 'kicad'}:/input:ro",
                "-v",
                f"{run / 'cam'}:/out",
                IMAGE,
                "kicad-cli",
                "pcb",
                "drc",
                "--format",
                "json",
                "--severity-all",
                "--exit-code-violations",
                "--output",
                "/out/drc.json",
                f"/input/{design}.kicad_pcb",
            ],
            run / "drc.log",
            (0, 5),
        )
        if inventory(run / "kicad") != before:
            raise ValueError("Generated CAD changed")
        drc = json.loads((run / "cam/drc.json").read_text())
        observation = json.loads((run / "physical-observation.json").read_text())
        row = {
            "experiment": index,
            "design": design,
            "fresh_generated_state": True,
            "input_unchanged": True,
            "files": inventory(run),
            "route_requests": len(observation["routes"]),
            "realized_requests": sum(r["realized"] for r in observation["routes"]),
            "via_count": len(observation["vias"]),
            "unconnected_items": len(drc["unconnected_items"]),
            "violations_by_type": dict(Counter(v["type"] for v in drc["violations"])),
        }
        pipeline["runs"].append(row)
        # Retain raw downstream findings and capture; never substitute endpoint accounting.
        write(
            f"experiment-{index}.json",
            {"summary": row, "drc": drc, "physical_observation": observation},
        )
        write("pipeline.json", pipeline)
        print(row | {"files": "inventory recorded"}, flush=True)
    command(
        [
            "jitx",
            "design",
            "export",
            "m1-electrical-graph",
            ELECTRICAL,
            "--output",
            str(OUTPUT / "c2.json"),
        ],
        OUTPUT / "c2.log",
    )
    raw = json.loads((OUTPUT / "c2.json").read_text())
    _, parity = evaluate(raw, *load_inputs())
    if parity["result"] != "PASS":
        raise ValueError(parity)
    component_ports = {p["identity"] for c in raw["components"] for p in c["ports"]}

    def memberships(graph):
        return sorted(
            (n["name"] or "", sorted(set(n["members"]) & component_ports))
            for n in graph["nets"]
            if set(n["members"]) & component_ports
        )

    for index in (1, 2):
        wrapper = json.loads((OUTPUT / f"experiment-{index}/electrical-graph.json").read_text())
        if raw["components"] != wrapper["components"] or memberships(raw) != memberships(wrapper):
            raise ValueError("C4B5 changed C2 component topology")
    if sources != {name: digest((PROJECT / name).read_bytes()) for name in sources}:
        raise ValueError("Source changed during experiments")
    write(
        "reconciliation.json",
        {
            "electrical_parity": parity,
            "both_wrapper_topologies_preserved": True,
            "complete_routing": False,
            "two_fresh_same_source_successful_generations": "not applicable: incomplete candidates",
            "cam": "not generated: incomplete routing",
        },
    )
    write("pipeline.json", pipeline)


if __name__ == "__main__":
    main()
