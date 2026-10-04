"""One-way supported C4B2 pipeline. Never modify the generated KiCad input.

Run from hardware/jitx in the existing locked environment. Only ignored fixture
state is removed. Historical C4B evidence is read, never regenerated/overwritten.
"""

import importlib.metadata
import json
import os
import shutil
import subprocess
from pathlib import Path

from physical.reproduce import DESIGN, ELECTRICAL, GENERATED, PROJECT, digest

OUTPUT = PROJECT / "designs/c4b2"
EVIDENCE = PROJECT / "physical/c4b2-evidence"
IMAGE = "kicad/kicad:9.0.9"
LAYERS = "F.Cu,B.Cu,F.Mask,B.Mask,F.Paste,B.Paste,F.SilkS,B.SilkS,Edge.Cuts"


def inventory(root: Path) -> dict:
    return {
        str(p.relative_to(root)): {"bytes": p.stat().st_size, "sha256": digest(p.read_bytes())}
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def main() -> None:
    EVIDENCE.mkdir(exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    historical = json.loads((PROJECT / "physical/evidence/build-manifest.json").read_text())
    sources = {name: digest((PROJECT / name).read_bytes()) for name in historical["source_sha256"]}
    if sources != historical["source_sha256"]:
        raise ValueError("Historical C4B source/configuration changed")
    automation = {
        str(p.relative_to(PROJECT)): digest(p.read_bytes())
        for p in sorted((PROJECT / "physical").glob("*c4b2*.py"))
    }
    commands = []

    def command(args: list[str], log: Path, accepted: tuple = (0,)) -> str:
        result = subprocess.run(args, cwd=PROJECT, capture_output=True, timeout=180, check=False)
        log.write_bytes(result.stdout + result.stderr)
        commands.append(
            {"argv": args, "returncode": result.returncode, "log": str(log.relative_to(PROJECT))}
        )
        if result.returncode not in accepted:
            raise RuntimeError(f"Supported command failed: {args}; see {log}")
        return result.stdout.decode()

    versions = {p: importlib.metadata.version(p) for p in ("jitx", "jitxlib-standard")}
    if versions != {"jitx": "4.4.3", "jitxlib-standard": "4.4.0"}:
        raise ValueError(versions)
    runtime = json.loads(command(["jitx", "runtime", "introspect"], OUTPUT / "runtime.json"))
    if runtime["version"] != "4.4.2":
        raise ValueError("Runtime changed")
    versions["runtime"] = runtime["version"]
    versions["kicad"] = command(
        ["docker", "run", "--rm", IMAGE, "kicad-cli", "version"], OUTPUT / "kicad-version.log"
    ).strip()
    if versions["kicad"] != "9.0.9":
        raise ValueError("KiCad changed")
    image_id = command(
        ["docker", "image", "inspect", IMAGE, "--format", "{{.Id}}"], OUTPUT / "image-id.log"
    ).strip()
    runs = []
    for index in (1, 2):
        run = OUTPUT / f"run-{index}"
        command(["jitx", "runtime", "stop"], OUTPUT / f"runtime-stop-{index}.log")
        if GENERATED.exists():
            shutil.rmtree(GENERATED)
        if run.exists():
            shutil.rmtree(run)
        run.mkdir()
        command(["jitx", "runtime", "start", "--background"], run / "runtime-start.log")
        command(["jitx", "design", "build", DESIGN, "--no-dependency-check"], run / "build.log")
        command(
            ["jitx", "design", "export", "physical-qualification", DESIGN, "--output", str(run)],
            run / "capture.log",
        )
        command(["jitx", "design", "export", "legacy-kicad", DESIGN], run / "kicad-export.log")
        shutil.copytree(GENERATED / "kicad", run / "kicad")
        input_before = inventory(run / "kicad")
        (run / "cam").mkdir()
        docker = [
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
        ]
        pcb = f"/input/{DESIGN}.kicad_pcb"
        command(
            [
                *docker,
                "drc",
                "--format",
                "json",
                "--severity-all",
                "--exit-code-violations",
                "--output",
                "/out/drc.json",
                pcb,
            ],
            run / "drc.log",
            (0, 5),
        )
        command(
            [*docker, "export", "gerbers", "--layers", LAYERS, "--output", "/out/gerber/", pcb],
            run / "gerber.log",
        )
        command(
            [
                *docker,
                "export",
                "drill",
                "--format",
                "excellon",
                "--excellon-units",
                "mm",
                "--excellon-separate-th",
                "--generate-report",
                "--report-path",
                "/out/drill-report.txt",
                "--output",
                "/out/drill/",
                pcb,
            ],
            run / "drill.log",
        )
        command(
            [
                *docker,
                "export",
                "pos",
                "--format",
                "csv",
                "--units",
                "mm",
                "--side",
                "both",
                "--output",
                "/out/positions.csv",
                pcb,
            ],
            run / "pos.log",
        )
        if input_before != inventory(run / "kicad"):
            raise ValueError("CAM altered generated KiCad input")
        for name in ("drc.json", "positions.csv", "drill-report.txt"):
            shutil.copyfile(run / "cam" / name, EVIDENCE / f"run-{index}-{name}")
        runs.append({"run": index, "input_unchanged": True, "files": inventory(run)})
        print(
            f"Run {index}: fresh build, capture, legacy-kicad, DRC, Gerber, drill, PnP done",
            flush=True,
        )
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
    if sources != {name: digest((PROJECT / name).read_bytes()) for name in sources}:
        raise ValueError("C4B source changed during generation")
    if automation != {name: digest((PROJECT / name).read_bytes()) for name in automation}:
        raise ValueError("C4B2 automation changed during generation")
    manifest = {
        "issue": 45,
        "baseline": "d085e540aefc76e2dd56b614b2c8141f42facbe9",
        "branch": "eda-002c4b2-headless-kicad-cam",
        "versions": versions,
        "image": IMAGE,
        "image_id": image_id,
        "source_sha256": sources,
        "automation_sha256": automation,
        "runs": runs,
        "commands": commands,
        "historical_source_unchanged": True,
    }
    (EVIDENCE / "pipeline.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
