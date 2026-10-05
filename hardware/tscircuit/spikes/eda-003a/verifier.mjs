import assert from "node:assert/strict";

export const TOLERANCE = 0.001;
export const expectedPads = [
  { pin: "1", x: -0.9375, y: 0.95 },
  { pin: "2", x: -0.9375, y: -0.95 },
  { pin: "3", x: 0.9375, y: 0 },
];
export function close(actual, expected, label) {
  assert.ok(
    Number.isFinite(actual) && Math.abs(actual - expected) <= TOLERANCE,
    `${label}: expected ${expected}, received ${actual}`,
  );
}

// Literal source-geometry oracle. These are assertions, never converter output.
// KiCad polygon order: implicit straight links between successive arcs.
const outer = [
  [1.8, -1.6, 0, -90],
  [-1.8, -1.6, -90, -180],
  [-1.8, 1.6, 180, 90],
  [1.8, 1.6, 90, 0],
];
const notch = [
  [1.8, 0.5, 0, -90],
  [0.4, 0.1, 90, 180],
  [0.4, -0.1, 180, 270],
  [1.8, -0.5, 90, 0],
];
export function expectedOutline(layer) {
  return [...outer, ...(layer === "top" ? notch : [])].flatMap(
    ([cx, cy, start, end]) =>
      Array.from({ length: 65 }, (_, i) => {
        const a = ((start + ((end - start) * i) / 64) * Math.PI) / 180;
        return { x: cx + 0.2 * Math.cos(a), y: -(cy + 0.2 * Math.sin(a)) };
      }),
  );
}
function pointSegmentDistance(p, a, b) {
  const dx = b.x - a.x,
    dy = b.y - a.y;
  const length2 = dx * dx + dy * dy;
  const t = length2
    ? Math.max(0, Math.min(1, ((p.x - a.x) * dx + (p.y - a.y) * dy) / length2))
    : 0;
  return Math.hypot(p.x - a.x - t * dx, p.y - a.y - t * dy);
}
function boundaryDistance(a, b) {
  return Math.max(
    ...a
      .flatMap((p, i) => {
        const next = a[(i + 1) % a.length];
        return [p, { x: (p.x + next.x) / 2, y: (p.y + next.y) / 2 }];
      })
      .map((p) =>
        Math.min(
          ...b.map((q, i) => pointSegmentDistance(p, q, b[(i + 1) % b.length])),
        ),
      ),
  );
}
export function verifyGeometry(elements) {
  const checks = {};
  const run = (name, f) => {
    try {
      f();
      checks[name] = { pass: true };
    } catch (e) {
      checks[name] = { pass: false, reason: e.message };
    }
  };
  const of = (type) => elements.filter((e) => e.type === type);
  const pads = of("pcb_smtpad"),
    pth = of("pcb_plated_hole"),
    npth = of("pcb_hole");
  const pad = (pin) => pads.find((p) => p.port_hints?.includes(pin));
  run("smd", () => {
    assert.equal(pads.length, 3, "SMD count");
    for (const e of expectedPads) {
      const p = pad(e.pin);
      assert.ok(p, `missing SMD ${e.pin}`);
      assert.deepEqual(p.port_hints, [e.pin]);
      assert.equal(p.layer, "top");
      assert.equal(p.shape, "rect");
      close(p.ccw_rotation ?? 0, 0, "SMD rotation");
      for (const [k, v] of Object.entries({
        x: e.x,
        y: e.y,
        width: 1.475,
        height: 0.6,
      }))
        close(p[k], v, `SMD ${e.pin} ${k}`);
    }
  });
  run("roundedPadCopper", () => {
    for (const e of expectedPads)
      close(pad(e.pin)?.corner_radius, 0.15, `SMD ${e.pin} corner_radius`);
  });
  run("pth", () => {
    assert.equal(pth.length, 1, "PTH count");
    assert.equal(pth[0].shape, "circle");
    assert.deepEqual(pth[0].port_hints, ["3"]);
    assert.deepEqual(pth[0].layers, ["top", "bottom"]);
    for (const [k, v] of Object.entries({
      x: 2.3,
      y: 0,
      hole_diameter: 0.3,
      outer_diameter: 0.6,
    }))
      close(pth[0][k], v, `PTH ${k}`);
  });
  run("npth", () => {
    assert.equal(npth.length, 2, "NPTH count");
    for (const x of [-5.08, 5.08]) {
      const h = npth.find((h) => Math.abs(h.x - x) <= TOLERANCE);
      assert.ok(h, `missing NPTH ${x}`);
      assert.equal(h.hole_shape, "circle");
      close(h.y, 0, "NPTH y");
      close(h.hole_diameter, 1.7, "NPTH diameter");
      assert.ok(
        !h.pcb_port_id && !h.outer_diameter,
        "NPTH must not carry plated copper/port semantics",
      );
    }
  });
  run("duplicatePin3", () => {
    const s = pad("3"),
      h = pth[0];
    assert.ok(s && h);
    const ports = of("pcb_port"),
      sp = ports.find((p) => p.pcb_port_id === s.pcb_port_id),
      hp = ports.find((p) => p.pcb_port_id === h.pcb_port_id);
    assert.ok(sp && hp, "both physical pin-3 ports required");
    assert.notEqual(sp.pcb_port_id, hp.pcb_port_id);
    assert.ok(sp.source_port_id);
    assert.equal(sp.source_port_id, hp.source_port_id);
    close(sp.x, s.x, "SMD3 port x");
    close(sp.y, s.y, "SMD3 port y");
    close(hp.x, h.x, "PTH3 port x");
    close(hp.y, h.y, "PTH3 port y");
    assert.deepEqual(sp.layers, ["top"]);
    assert.deepEqual(hp.layers, ["top", "bottom"]);
  });
  run("transform", () => {
    const cs = of("pcb_component");
    assert.equal(cs.length, 1);
    close(cs[0].center.x, 0, "origin x");
    close(cs[0].center.y, 0, "origin y");
    close(cs[0].rotation, 0, "rotation");
    for (const e of expectedPads) {
      close(pad(e.pin)?.x, e.x, "X unchanged");
      close(pad(e.pin)?.y, e.y, "Y inverted");
    }
    for (const [items, xs] of [
      [pth, [2.3]],
      [npth, [-5.08, 5.08]],
    ]) {
      assert.equal(items.length, xs.length);
      for (const x of xs) {
        const p = items.find((p) => Math.abs(p.x - x) <= TOLERANCE);
        assert.ok(p);
        close(p.y, 0, "hole transform y");
      }
    }
  });
  const keepouts = of("pcb_keepout");
  for (const layer of ["top", "bottom"])
    run(`${layer}Keepout`, () => {
      assert.equal(
        keepouts.length,
        2,
        "both material keepout records required",
      );
      const k = keepouts.find((k) => k.layers?.includes(layer));
      assert.ok(k, `missing ${layer} keepout`);
      assert.ok(!k.warning_only, "keepout must enforce exclusion");
      assert.equal(k.allow_traces, true);
      assert.equal(k.allow_placements, true);
      assert.equal(
        k.shape,
        "outline",
        "exact source polygon required; native conservative rectangle is not identical",
      );
      assert.ok(Array.isArray(k.outline) && k.outline.length >= 4);
      for (const p of k.outline)
        assert.ok(Number.isFinite(p.x) && Number.isFinite(p.y));
      close(k.stroke_width, 0, "filled polygon boundary stroke");
      const expected = expectedOutline(layer);
      assert.ok(
        Math.max(
          boundaryDistance(expected, k.outline),
          boundaryDistance(k.outline, expected),
        ) <= TOLERANCE,
        "keepout arc/notch boundary differs beyond 0.001 mm",
      );
    });
  return { pass: Object.values(checks).every((c) => c.pass), checks };
}
export function safetyGate(geometry, warnings) {
  assert.ok(geometry.pass, "manufacturing geometry fidelity failed");
  assert.ok(Array.isArray(warnings), "warnings unavailable");
  assert.equal(
    warnings.length,
    0,
    "converter warnings require explicit review",
  );
}
