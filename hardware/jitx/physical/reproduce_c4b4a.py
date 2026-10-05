"""Supported one-way coupon generation; raw CAD/CAM are never patched."""

import importlib.metadata
import json
import os
import shutil
import subprocess
from pathlib import Path

from physical.reproduce import PROJECT, digest
from physical.reproduce_c4b2 import IMAGE, LAYERS, inventory

DESIGN = "he_piantor_42_jitx.usb_dfm_coupon.USBDFMCoupon"
OUTPUT = PROJECT / "designs/c4b4a"
EVIDENCE = PROJECT / "physical/c4b4a-evidence"
BASELINE = "e4d6a54252ebf698006d1221e9620fb5f13569ef"


def write(name: str, value: dict) -> None:
    (EVIDENCE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def protected() -> None:
    preflight = json.loads((EVIDENCE / "preflight.json").read_text())
    for name, expected in preflight["protected_files"].items():
        if digest((PROJECT.parents[1] / name).read_bytes()) != expected:
            raise ValueError(f"Protected evidence changed: {name}")
    for name, expected in preflight["accepted_source_sha256"].items():
        if digest((PROJECT / name).read_bytes()) != expected:
            raise ValueError(f"Accepted source changed: {name}")


def main() -> None:
    protected()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    sources = {
        str(p.relative_to(PROJECT)): digest(p.read_bytes())
        for p in [
            PROJECT / "he_piantor_42_jitx/usb_dfm_coupon.py",
            *sorted((PROJECT / "physical").glob("*c4b4a.py")),
        ]
    }
    commands = []

    def command(args: list[str], log: Path, accepted=(0,)) -> str:
        result = subprocess.run(args, cwd=PROJECT, capture_output=True, timeout=180, check=False)
        log.write_bytes(result.stdout + result.stderr)
        commands.append({"argv": args, "returncode": result.returncode, "log": str(log)})
        if result.returncode not in accepted:
            raise RuntimeError(f"Command failed: {args}; see {log}")
        return result.stdout.decode()

    versions = {p: importlib.metadata.version(p) for p in ("jitx", "jitxlib-standard")}
    versions["runtime"] = json.loads(
        command(["jitx", "runtime", "introspect"], OUTPUT / "runtime.json")
    )["version"]
    versions["kicad"] = command(
        ["docker", "run", "--rm", IMAGE, "kicad-cli", "version"], OUTPUT / "kicad.log"
    ).strip()
    if versions != {
        "jitx": "4.4.3",
        "jitxlib-standard": "4.4.0",
        "runtime": "4.4.2",
        "kicad": "9.0.9",
    }:
        raise ValueError(versions)
    image_id = command(
        ["docker", "image", "inspect", IMAGE, "--format", "{{.Id}}"], OUTPUT / "image.log"
    ).strip()
    preflight = json.loads((EVIDENCE / "preflight.json").read_text())
    if image_id != preflight["image_id"]:
        raise ValueError("Pinned image changed")
    command(["python", "-m", "physical.measure_c4b4a"], OUTPUT / "measurement.log")
    runs = []
    for index in (1, 2):
        run = OUTPUT / f"run-{index}"
        command(["jitx", "runtime", "stop"], OUTPUT / f"stop-{index}.log")
        generated = PROJECT / "designs" / DESIGN
        for path in (generated, run):
            if path.exists():
                shutil.rmtree(path)
        run.mkdir()
        command(["jitx", "runtime", "start", "--background"], run / "runtime.log")
        command(["jitx", "design", "build", DESIGN, "--no-dependency-check"], run / "build.log")
        command(["jitx", "design", "export", "legacy-kicad", DESIGN], run / "export.log")
        shutil.copytree(generated / "kicad", run / "kicad")
        before = inventory(run / "kicad")
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
            [
                *docker,
                "export",
                "gerbers",
                "--layers",
                LAYERS,
                "--output",
                "/out/gerber/",
                pcb,
            ],
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
        if before != inventory(run / "kicad"):
            raise ValueError("Generated KiCad input changed")
        for name in ("drc.json", "drill-report.txt"):
            shutil.copyfile(run / "cam" / name, EVIDENCE / f"run-{index}-{name}")
        runs.append({"run": index, "input_unchanged": True, "files": inventory(run)})
        print(f"Run {index}: build/export/Gerber/Excellon complete", flush=True)
    protected()
    if sources != {name: digest((PROJECT / name).read_bytes()) for name in sources}:
        raise ValueError("Coupon source/automation changed during generation")
    write(
        "pipeline.json",
        {
            "issue": 49,
            "baseline": BASELINE,
            "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PROJECT)
            .decode()
            .strip(),
            "versions": versions,
            "image": IMAGE,
            "image_id": image_id,
            "source_sha256": sources,
            "accepted_source_sha256": preflight["accepted_source_sha256"],
            "commands": commands,
            "runs": runs,
            "qualification_only": True,
            "geometry_postprocessing": False,
        },
    )


if __name__ == "__main__":
    main()
