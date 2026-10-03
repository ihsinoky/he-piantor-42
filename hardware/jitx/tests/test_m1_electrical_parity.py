"""Real runtime parity plus fault injections against those real exported facts."""

import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from parity.m1 import evaluate, load_inputs

PROJECT_ROOT = Path(__file__).resolve().parents[1]
M1 = "he_piantor_42_jitx.m1.M1FourKeyElectrical"


def export_graph(output: Path) -> dict:
    subprocess.run(
        ["jitx", "design", "export", "m1-electrical-graph", M1, "--output", str(output)],
        cwd=PROJECT_ROOT,
        check=True,
    )
    return json.loads(output.read_text())


class M1ElectricalParityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract, cls.mapping = load_inputs()
        with tempfile.TemporaryDirectory() as directory:
            cls.first = export_graph(Path(directory) / "first.json")
            cls.second = export_graph(Path(directory) / "second.json")

    def assert_failure(self, raw: dict, message: str, mapping: dict | None = None) -> None:
        _, result = evaluate(raw, self.contract, mapping or self.mapping)
        self.assertEqual(result["result"], "FAIL")
        self.assertIn(message, "\n".join(result["differences"]))

    def test_independent_real_exports_are_deterministic_and_pass(self) -> None:
        self.assertEqual(self.first, self.second)
        first_graph, first_result = evaluate(self.first, self.contract, self.mapping)
        second_graph, second_result = evaluate(self.second, self.contract, self.mapping)
        self.assertEqual(first_graph, second_graph)
        self.assertEqual(first_result, second_result)
        self.assertEqual(first_result["differences"], [])
        self.assertEqual(first_result["result"], "PASS")
        self.assertEqual(
            [
                first_result[k]
                for k in [
                    "compared_component_count",
                    "compared_endpoint_count",
                    "compared_named_net_count",
                    "compared_edge_count",
                    "direct_link_count",
                    "intentional_nc_count",
                ]
            ],
            [68, 200, 43, 185, 4, 7],
        )
        assert first_graph is not None
        self.assertTrue(first_graph["geometry_excluded"])
        self.assertNotIn("capturedGeometry", self.first)
        self.assertEqual(len(first_graph["extra_unconnected_endpoints"]), 23)
        values = {c["reference"]: c["value"] for c in first_graph["components"]}
        self.assertEqual(values["D_POWER"], "green LED")
        self.assertEqual(values["D_STATUS"], "amber LED")
        for ref in ["SW_BOOT", "SW_RUN"]:
            self.assertEqual(values[ref], "normally-open pushbutton")
        for component in first_graph["components"]:
            if component["mpn"] is not None or component["reference"].startswith("TP_"):
                self.assertIsNone(component["value"])

    def test_rejects_missing_duplicate_unknown_components_and_endpoints(self) -> None:
        for mutation, message in [
            (lambda r: r["components"].pop(), "component population"),
            (lambda r: r["components"].append(r["components"][0]), "component population"),
            (lambda r: r["ports"].pop(), "endpoint inventory"),
            (lambda r: r["ports"].append(r["ports"][0]), "Duplicate built endpoint"),
            (lambda r: r["ports"].append({"identity": "circuit.U_MCU.UNKNOWN"}), "unknown="),
            (lambda r: r["components"][0]["ports"].pop(), "missing/unknown/duplicate ports"),
        ]:
            with self.subTest(message=message):
                raw = copy.deepcopy(self.first)
                mutation(raw)
                self.assert_failure(raw, message)

    def test_rejects_net_opens_shorts_nc_and_unused_gpio_connections(self) -> None:
        raw = copy.deepcopy(self.first)
        next(n for n in raw["nets"] if n["name"] == "ADC_SENSE")["members"].remove(
            "circuit.U_MCU.GPIO26"
        )
        self.assert_failure(raw, "Expected connected endpoint floats: U_MCU.ADC_SENSE")
        for endpoint, message in [
            ("circuit.J_USB.A8", "Intentional NC connected: J_USB.A8"),
            ("circuit.U_MCU.GPIO0", "Unused physical RP2040 GPIO"),
        ]:
            raw = copy.deepcopy(self.first)
            next(n for n in raw["nets"] if n["name"] == "VBUS")["members"].append(endpoint)
            self.assert_failure(raw, message)
        raw = copy.deepcopy(self.first)
        a = next(n for n in raw["nets"] if n["name"] == "USB_DP")
        b = next(n for n in raw["nets"] if n["name"] == "USB_DM")
        a["members"].extend(b["members"])
        raw["nets"].remove(b)
        self.assert_failure(raw, "Net USB_DM:")
        raw = copy.deepcopy(self.first)
        raw["nets"][0]["members"].append("circuit.TP_UNKNOWN.pin1")
        self.assert_failure(raw, "Unknown net endpoints")
        raw = copy.deepcopy(self.first)
        raw["nets"][0]["members"].append(raw["nets"][0]["members"][0])
        self.assert_failure(raw, "Duplicate net membership")

    def test_rejects_direct_link_short_and_open(self) -> None:
        raw = copy.deepcopy(self.first)
        direct = next(n for n in raw["nets"] if "circuit.J_USB.A5" in n["members"])
        direct["members"].remove("circuit.R_CC1.p1")
        self.assert_failure(raw, "Direct link missing or shorted")
        raw = copy.deepcopy(self.first)
        direct = next(n for n in raw["nets"] if "circuit.J_USB.A5" in n["members"])
        direct["members"].append("circuit.J_USB.A8")
        self.assert_failure(raw, "Direct link missing or shorted")

    def test_rejects_missing_unresolved_or_duplicate_named_nets(self) -> None:
        for kind in ["missing", "unresolved", "duplicate"]:
            raw = copy.deepcopy(self.first)
            cc1 = next(d for d in raw["named_net_declarations"] if d["name"] == "CC1")
            if kind == "missing":
                raw["named_net_declarations"].remove(cc1)
            elif kind == "unresolved":
                cc1["resolved"] = False
            else:
                raw["named_net_declarations"].append(cc1)
            self.assert_failure(raw, "Named net")

    def test_rejects_value_identity_model_and_pin_assignment_regressions(self) -> None:
        for reference, key, value, message in [
            ("R_ADC_TOP", "value", {"unit": "ohm", "magnitude": 10000}, "R_ADC_TOP: expected"),
            ("C_XIN", "value", {"unit": "farad", "magnitude": 15e-9}, "C_XIN: expected"),
            ("U_FLASH", "mpn", "WRONG", "U_FLASH: mpn"),
            ("U_MCU", "supplier_part_number", "C0000", "U_MCU: supplier"),
            ("D_POWER", "mpn", "invented", "generic component claims"),
            ("U_MCU", "type", "unapproved.Model", "expected accepted model"),
        ]:
            raw = copy.deepcopy(self.first)
            component = next(
                c for c in raw["components"] if c["identity"] == f"circuit.{reference}"
            )
            component[key] = value
            self.assert_failure(raw, message)
        raw = copy.deepcopy(self.first)
        mcu = next(c for c in raw["components"] if c["identity"] == "circuit.U_MCU")
        pins = mcu["physical_pin_assignments"]
        pins["circuit.U_MCU.GPIO2"], pins["circuit.U_MCU.GPIO3"] = (
            pins["circuit.U_MCU.GPIO3"],
            pins["circuit.U_MCU.GPIO2"],
        )
        self.assert_failure(raw, "logical-to-physical pin assignments differ")

    def test_normalization_fails_closed_and_cannot_hide_a_gpio_swap(self) -> None:
        for kind in ["missing", "duplicate", "swap"]:
            mapping = copy.deepcopy(self.mapping)
            ports = mapping["components"]["circuit.U_MCU"]["ports"]
            if kind == "missing":
                ports.pop("circuit.U_MCU.GPIO2")
            elif kind == "duplicate":
                ports["circuit.U_MCU.GPIO2"] = ports["circuit.U_MCU.GPIO3"]
            else:
                ports["circuit.U_MCU.GPIO2"], ports["circuit.U_MCU.GPIO3"] = (
                    ports["circuit.U_MCU.GPIO3"],
                    ports["circuit.U_MCU.GPIO2"],
                )
            self.assert_failure(
                self.first,
                {
                    "missing": "cover the frozen",
                    "duplicate": "Duplicate endpoint alias",
                    "swap": "logical-to-physical",
                }[kind],
                mapping,
            )

    def test_geometry_is_excluded_from_verdict(self) -> None:
        raw = copy.deepcopy(self.first)
        raw["capturedGeometry"] = [{"unrelated_geometry": "deliberately different"}]
        _, result = evaluate(raw, self.contract, self.mapping)
        self.assertEqual(result["result"], "PASS")
