import assert from "node:assert/strict";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";
import { KicadFootprintToCircuitJsonConverter as Upstream } from "kicad-to-circuit-json";
import { parseKicadMod } from "kicadts";
import { verifyGeometry, safetyGate } from "./verifier.mjs";

const here = new URL("./", import.meta.url);
const matrix = JSON.parse(
  readFileSync(new URL("evidence/version-matrix.json", here)),
);
const project = new URL("../../", here);
const source = readFileSync(
  new URL(
    "../../../lib/third_party/marbastlib-he.pretty/SW_MX_HE_0deg_1u.kicad_mod",
    here,
  ),
);
const sha = (b) => createHash("sha256").update(b).digest("hex");
assert.equal(
  sha(source),
  matrix.source.sha256,
  "historical source must not change",
);
assert.equal(
  sha(readFileSync(new URL("package.json", project))),
  matrix.project.manifest_sha256,
  "production manifest changed",
);
assert.equal(
  sha(readFileSync(new URL("package-lock.json", project))),
  matrix.project.lock_sha256,
  "production lock changed",
);
const packageVersion = (name) =>
  JSON.parse(readFileSync(new URL(`node_modules/${name}/package.json`, here)))
    .version;
assert.equal(packageVersion("kicad-to-circuit-json"), matrix.upstream.importer);
// Prove every external runtime import resolves inside the spike, not its parent.
const resolution = Object.fromEntries(
  matrix.upstream.external_runtime_imports.map((name) => {
    const resolved = fileURLToPath(import.meta.resolve(name));
    assert.ok(
      resolved.startsWith(fileURLToPath(new URL("node_modules/", here))),
      `runtime import escaped spike: ${name}`,
    );
    return [name, packageVersion(name)];
  }),
);
const write = (name, data) =>
  writeFileSync(
    new URL(`evidence/${name}.json`, here),
    JSON.stringify(data, null, 2) + "\n",
  );
mkdirSync(new URL("evidence/", here), { recursive: true });
function convert(C, bytes) {
  const c = new C(),
    consoleWarnings = [],
    consoleErrors = [];
  const oldWarn = console.warn,
    oldError = console.error;
  try {
    console.warn = (...args) =>
      consoleWarnings.push(args.map(String).join(" "));
    console.error = (...args) => consoleErrors.push(args.map(String).join(" "));
    c.addFile("SW_MX_HE_0deg_1u.kicad_mod", bytes.toString());
    c.runUntilFinished();
    return {
      converter: c,
      output: c.getOutput(),
      warnings: typeof c.getWarnings === "function" ? c.getWarnings() : null,
      consoleWarnings,
      consoleErrors,
    };
  } finally {
    console.warn = oldWarn;
    console.error = oldError;
  }
}
const summarize = (r) => ({
  conversion_succeeded: true,
  counts: Object.fromEntries(
    [
      ...new Set([
        ...r.output.map((e) => e.type),
        "pcb_keepout",
        "pcb_copper_pour",
        "source_port",
        "cad_component",
      ]),
    ]
      .sort()
      .map((t) => [t, r.output.filter((e) => e.type === t).length]),
  ),
  material_records: r.output.filter((e) =>
    [
      "pcb_smtpad",
      "pcb_plated_hole",
      "pcb_hole",
      "pcb_port",
      "source_port",
      "pcb_component",
      "pcb_keepout",
      "source_component_internal_connection",
    ].includes(e.type),
  ),
  geometry: verifyGeometry(r.output),
  warnings: r.warnings,
  console_warnings: r.consoleWarnings,
  console_errors: r.consoleErrors,
  source_ports_resolve: r.output
    .filter((e) => e.type === "pcb_port")
    .every((p) =>
      r.output.some(
        (e) =>
          e.type === "source_port" && e.source_port_id === p.source_port_id,
      ),
    ),
});
const parsed = parseKicadMod(source.toString());
const zones = parsed.zones.map((z) => ({
  name: z.name,
  uuid: z.uuid.value,
  layers: z.layer?.names ?? z.layers?.names,
  permissions: Object.fromEntries(
    ["tracks", "vias", "pads", "copperpour", "footprints"].map((k) => [
      k,
      z.keepout[k],
    ]),
  ),
  arcs: z.polygons[0].pts.points.map((a) => ({
    start: [a.start.x, a.start.y],
    mid: [a.mid.x, a.mid.y],
    end: [a.end.x, a.end.y],
  })),
}));
assert.equal(zones.length, 2);
assert.deepEqual(
  zones.map((z) => z.arcs.length),
  [8, 4],
);
assert.deepEqual(zones[0].layers, ["F.Cu"]);
assert.equal(zones[1].layers[0], "B.Cu");
assert.equal(zones[1].layers.length, 31);
for (const z of zones)
  assert.deepEqual(z.permissions, {
    tracks: "allowed",
    vias: "allowed",
    pads: "allowed",
    copperpour: "not_allowed",
    footprints: "allowed",
  });
const sourcePadDetails = parsed.fpPads.map((p) => ({
  number: p.number,
  shape: p.shape,
  roundrect_ratio: p.roundrectRatio ?? null,
  zone_connect: p.zoneConnect ?? null,
}));
assert.equal(sourcePadDetails.filter((p) => p.zone_connect === 2).length, 2);
assert.equal(parsed.models.length, 1);
const up = convert(Upstream, source);
const { KicadFootprintToCircuitJsonConverter: Project } = await import(
  new URL("node_modules/kicad-to-circuit-json/dist/index.js", project)
);
assert.equal(
  JSON.parse(
    readFileSync(
      new URL("node_modules/kicad-to-circuit-json/package.json", project),
    ),
  ).version,
  matrix.project.importer.version,
);
const pr = convert(Project, source);
write("project-result", {
  version: matrix.project.importer.version,
  ...summarize(pr),
});
write("upstream-result", {
  version: matrix.upstream.importer,
  isolated_runtime_resolution: resolution,
  ...summarize(up),
});
const mini = convert(
  Upstream,
  readFileSync(new URL("keepout-repro.kicad_mod", here)),
);
write("geometry-comparison", {
  tolerance_mm: 0.001,
  oracle:
    "HallKey.tsx and verify-native-hall-checkpoint-a.tsx for pad/hole dimensions; exact unaltered KiCad zones for keepout polygons; KiCad PADSTACK::RoundRectRadius for corner radius",
  source_sha256: sha(source),
  source_keepouts: zones,
  source_pad_attributes: sourcePadDetails,
  native_oracle_y: "pin1=-0.95; pin2=+0.95",
  import_transform: "x_cj=x_kicad; y_cj=-y_kicad; origin=(0,0); rotation=0",
  native_keepout_envelope_mm: [4, 3.6],
  native_envelope_is_not_exact_polygon: true,
  project: verifyGeometry(pr.output),
  upstream: verifyGeometry(up.output),
  mini_reproducer: {
    source: "keepout-repro.kicad_mod",
    pcb_keepouts: mini.output.filter((e) => e.type === "pcb_keepout"),
    warnings: mini.warnings,
  },
});
write("warnings", {
  upstream_surface: "getWarnings(): string[]",
  upstream: up.warnings,
  project: pr.warnings,
  console_warnings: up.consoleWarnings,
  console_errors: up.consoleErrors,
  specific_keepout_warning: up.warnings.some((w) => /keepout/i.test(w)),
  machine_gate:
    "reject warnings.length > 0; also independently reject geometry failures, including silent loss",
  supported_keepout_warning_case: "not applicable: keepout conversion fails",
  silent_material_losses: [
    "two copper-pour keepouts",
    "roundrect corner_radius 0.075 instead of 0.15 mm",
  ],
  other_observed_unsupported_source_constructs: [
    {
      construct: "pad 3 SMD and PTH zone_connect=2 (solid copper connection)",
      warning: false,
      assessment:
        "not represented on imported pad records; future pour behavior unqualified",
    },
    {
      construct: "model SOT-23.step",
      warning: false,
      assessment: "no cad_component; mechanical metadata loss",
    },
    {
      construct: "Dwgs.User and Eco2.User graphics",
      warning: false,
      assessment:
        "reference graphics omitted; not material copper/drill geometry",
    },
  ],
});
if (process.argv.includes("--raw")) {
  mkdirSync(new URL("raw/", here), { recursive: true });
  for (const [name, r] of [
    ["project", pr],
    ["upstream", up],
  ])
    writeFileSync(
      new URL(`raw/${name}.json`, here),
      JSON.stringify(r.output, null, 2) + "\n",
    );
}
console.log(
  JSON.stringify(
    {
      project: verifyGeometry(pr.output),
      upstream: verifyGeometry(up.output),
      warnings: up.warnings,
    },
    null,
    2,
  ),
);
if (process.argv.includes("--gate"))
  safetyGate(verifyGeometry(up.output), up.warnings);
