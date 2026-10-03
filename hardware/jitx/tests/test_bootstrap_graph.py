"""End-to-end assertions for the public JITX bootstrap graph exporter."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = "he_piantor_42_jitx.main.HePiantor42Bootstrap"


def export_graph(output: Path) -> dict:
    subprocess.run(
        [
            "jitx",
            "design",
            "export",
            "bootstrap-graph",
            BOOTSTRAP,
            "--output",
            str(output),
        ],
        cwd=PROJECT_ROOT,
        check=True,
    )
    return json.loads(output.read_text(encoding="utf-8"))


class BootstrapGraphTest(unittest.TestCase):
    def test_public_export_is_deterministic_and_preserves_bootstrap_connectivity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            first = export_graph(Path(temporary_directory) / "first.json")
            second = export_graph(Path(temporary_directory) / "second.json")

        self.assertEqual(first, second)
        self.assertEqual(
            first["components"],
            [
                {
                    "identity": "circuit.r1",
                    "type": "he_piantor_42_jitx.components.resistor.Resistor",
                    "ports": [
                        {"identity": "circuit.r1.p1", "type": "jitx.net.Port"},
                        {"identity": "circuit.r1.p2", "type": "jitx.net.Port"},
                    ],
                },
                {
                    "identity": "circuit.r2",
                    "type": "he_piantor_42_jitx.components.resistor.Resistor",
                    "ports": [
                        {"identity": "circuit.r2.p1", "type": "jitx.net.Port"},
                        {"identity": "circuit.r2.p2", "type": "jitx.net.Port"},
                    ],
                },
            ],
        )
        self.assertEqual(
            first["nets"],
            [
                {"name": None, "members": ["circuit.r1.p1", "circuit.r2.p1"]},
                {"name": None, "members": ["circuit.r1.p2", "circuit.r2.p2"]},
            ],
        )
