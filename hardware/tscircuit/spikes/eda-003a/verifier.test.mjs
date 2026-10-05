import assert from "node:assert/strict";
import nodeTest, { after } from "node:test";
import { readFileSync, writeFileSync } from "node:fs";
import { KicadFootprintToCircuitJsonConverter } from "kicad-to-circuit-json";
import {
  expectedPads,
  expectedOutline,
  verifyGeometry,
  safetyGate,
  close,
} from "./verifier.mjs";

const testResults = [];
function test(name, fn) {
  nodeTest(name, () => {
    try {
      fn();
      testResults.push({ name, pass: true });
    } catch (error) {
      testResults.push({ name, pass: false, reason: error.message });
      throw error;
    }
  });
}

// Entirely synthetic positive verifier fixture, not patched importer output.
function positiveFixture() {
  return [
    { type: "pcb_component", center: { x: 0, y: 0 }, rotation: 0 },
    ...expectedPads.flatMap((p) => [
      {
        type: "pcb_smtpad",
        shape: "rect",
        ...p,
        width: 1.475,
        height: 0.6,
        corner_radius: 0.15,
        layer: "top",
        port_hints: [p.pin],
        pcb_port_id: `s${p.pin}`,
      },
      {
        type: "pcb_port",
        pcb_port_id: `s${p.pin}`,
        source_port_id: `pin${p.pin}`,
        x: p.x,
        y: p.y,
        layers: ["top"],
      },
    ]),
    {
      type: "pcb_plated_hole",
      shape: "circle",
      x: 2.3,
      y: 0,
      hole_diameter: 0.3,
      outer_diameter: 0.6,
      port_hints: ["3"],
      layers: ["top", "bottom"],
      pcb_port_id: "h3",
    },
    {
      type: "pcb_port",
      pcb_port_id: "h3",
      source_port_id: "pin3",
      x: 2.3,
      y: 0,
      layers: ["top", "bottom"],
    },
    ...[-5.08, 5.08].map((x) => ({
      type: "pcb_hole",
      hole_shape: "circle",
      x,
      y: 0,
      hole_diameter: 1.7,
    })),
    ...["top", "bottom"].map((layer) => ({
      type: "pcb_keepout",
      shape: "outline",
      layers: [layer],
      allow_traces: true,
      allow_placements: true,
      stroke_width: 0,
      outline: expectedOutline(layer),
    })),
  ];
}
const negativeResults = [];
const cases = [
  [
    "missing SMD",
    "smd",
    (es) =>
      es.splice(
        es.findIndex((e) => e.type === "pcb_smtpad"),
        1,
      ),
  ],
  [
    "missing NPTH",
    "npth",
    (es) =>
      es.splice(
        es.findIndex((e) => e.type === "pcb_hole"),
        1,
      ),
  ],
  [
    "NPTH incorrectly plated",
    "npth",
    (es) => (es.find((e) => e.type === "pcb_hole").type = "pcb_plated_hole"),
  ],
  [
    "PTH incorrectly non-plated",
    "pth",
    (es) => (es.find((e) => e.type === "pcb_plated_hole").type = "pcb_hole"),
  ],
  [
    "geometry displacement",
    "smd",
    (es) => (es.find((e) => e.type === "pcb_smtpad").x += 0.002),
  ],
  [
    "missing keepout",
    "topKeepout",
    (es) =>
      es.splice(
        es.findIndex((e) => e.type === "pcb_keepout"),
        1,
      ),
  ],
  [
    "wrong keepout layer",
    "bottomKeepout",
    (es) =>
      (es.find(
        (e) => e.type === "pcb_keepout" && e.layers[0] === "bottom",
      ).layers = ["top"]),
  ],
  [
    "wrong keepout exclusion",
    "topKeepout",
    (es) => (es.find((e) => e.type === "pcb_keepout").warning_only = true),
  ],
  [
    "wrong keepout polygon",
    "topKeepout",
    (es) =>
      (es.find((e) => e.type === "pcb_keepout").outline =
        expectedOutline("bottom")),
  ],
  [
    "wrong rounded copper",
    "roundedPadCopper",
    (es) => (es.find((e) => e.type === "pcb_smtpad").corner_radius = 0.075),
  ],
  [
    "collapsed duplicate port",
    "duplicatePin3",
    (es) => (es.find((e) => e.type === "pcb_plated_hole").pcb_port_id = "s3"),
  ],
];
test("synthetic positive fixture passes every category", () =>
  safetyGate(verifyGeometry(positiveFixture()), []));
for (const [name, category, mutate] of cases)
  test(name, () => {
    const fixture = positiveFixture();
    mutate(fixture);
    const result = verifyGeometry(fixture);
    assert.equal(result.checks[category].pass, false);
    assert.throws(() => safetyGate(result, []));
    negativeResults.push({
      name,
      category,
      category_failed: !result.checks[category].pass,
      safety_gate_rejected: true,
    });
  });
test("tolerance accepts 0.0009 mm and rejects nonfinite geometry", () => {
  const fixture = positiveFixture();
  fixture.find((e) => e.type === "pcb_smtpad").x += 0.0009;
  assert.equal(verifyGeometry(fixture).checks.smd.pass, true);
  fixture.find((e) => e.type === "pcb_smtpad").x = NaN;
  assert.equal(verifyGeometry(fixture).checks.smd.pass, false);
});
test("warning surface is machine-gatable", () => {
  assert.throws(() =>
    safetyGate(verifyGeometry(positiveFixture()), ["unsupported keepout"]),
  );
  assert.throws(() => safetyGate(verifyGeometry(positiveFixture()), undefined));
});
function convert(source) {
  const converter = new KicadFootprintToCircuitJsonConverter();
  converter.addFile("test.kicad_mod", source);
  converter.runUntilFinished();
  return converter;
}
test("unaltered historical asset exposes silent losses", () => {
  const c = convert(
    readFileSync(
      new URL(
        "../../../lib/third_party/marbastlib-he.pretty/SW_MX_HE_0deg_1u.kicad_mod",
        import.meta.url,
      ),
      "utf8",
    ),
  );
  assert.deepEqual(c.getWarnings(), []);
  const result = verifyGeometry(c.getOutput());
  assert.equal(result.checks.topKeepout.pass, false);
  assert.equal(result.checks.bottomKeepout.pass, false);
  assert.equal(result.checks.roundedPadCopper.pass, false);
  assert.throws(() => safetyGate(result, c.getWarnings()));
});
test("standalone origin normalization and 90 degree rotation probe", () => {
  const c = convert(`(footprint "transform-probe" (layer "F.Cu") (at 10 20 90)
    (property "Reference" "U1" (at 0 0) (layer "F.SilkS"))
    (pad "1" smd rect (at 1 2 90) (size 1.475 0.6) (layers "F.Cu")))`);
  const es = c.getOutput(),
    p = es.find((e) => e.type === "pcb_smtpad"),
    component = es.find((e) => e.type === "pcb_component");
  close(component.center.x, 0, "probe origin x");
  close(component.center.y, 0, "probe origin y");
  close(component.rotation, 90, "probe component rotation");
  close(p.x, 2, "probe pad x");
  close(p.y, 1, "probe pad y");
  close(p.width, 0.6, "probe rotated width");
  close(p.height, 1.475, "probe rotated height");
  assert.deepEqual(c.getWarnings(), []);
});

test("minimal keepout reproducer parses but is silently omitted", () => {
  const c = convert(
    readFileSync(new URL("keepout-repro.kicad_mod", import.meta.url), "utf8"),
  );
  assert.equal(c.getOutput().filter((e) => e.type === "pcb_keepout").length, 0);
  assert.deepEqual(c.getWarnings(), []);
});
test("upstream warnings surface works for a supported diagnostic", () => {
  const c = convert(`(footprint "warning-probe" (layer "F.Cu")
    (property "Reference" "U1" (at 0 0) (layer "F.SilkS"))
    (property "Manufacturer" "Example" (at 0 0) (layer "F.Fab")))`);
  assert.ok(c.getWarnings().some((w) => /Manufacturer.*not supported/.test(w)));
});
after(() => {
  assert.equal(negativeResults.length, cases.length);
  writeFileSync(
    new URL("evidence/negative-controls.json", import.meta.url),
    JSON.stringify(
      {
        result:
          testResults.length === 18 && testResults.every((t) => t.pass)
            ? "PASS"
            : "FAIL",
        tests: testResults.length,
        passed: testResults.filter((t) => t.pass).length,
        failed: testResults.filter((t) => !t.pass),
        fault_injections: negativeResults,
        positive_fixture:
          "independent synthetic assertion fixture; never patched conversion output",
        supplemental_probes: [
          "0.0009 mm accepted; NaN rejected",
          "warnings and unavailable warnings rejected",
          "unaltered asset fails fidelity gate",
          "nonzero origin and 90 degree rotation",
          "minimal keepout silently dropped",
          "upstream Manufacturer diagnostic available",
        ],
      },
      null,
      2,
    ) + "\n",
  );
});
