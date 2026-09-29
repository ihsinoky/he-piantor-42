import fs from "node:fs"
import path from "node:path"
import process from "node:process"
import { createRequire } from "node:module"
import { fileURLToPath } from "node:url"
import { KicadFootprintToCircuitJsonConverter } from "kicad-to-circuit-json"

const here = path.dirname(fileURLToPath(import.meta.url))
const root = path.resolve(here, "../../..")
const inputPath = path.join(
  root,
  "hardware/lib/third_party/marbastlib-he.pretty/SW_MX_HE_0deg_1u.kicad_mod",
)
const evidenceDir = path.join(root, "hardware/tscircuit/footprint-evidence")
fs.mkdirSync(evidenceDir, { recursive: true })

const source = fs.readFileSync(inputPath, "utf8")
const require = createRequire(import.meta.url)
const converterEntry = require.resolve("kicad-to-circuit-json")
let packageJsonPath = path.join(path.dirname(converterEntry), "package.json")
while (!fs.existsSync(packageJsonPath) && path.dirname(packageJsonPath) !== packageJsonPath) {
  packageJsonPath = path.join(path.dirname(path.dirname(packageJsonPath)), "package.json")
}
const converterVersion = JSON.parse(fs.readFileSync(packageJsonPath, "utf8")).version
const warnings = []
let stats = null
const originalWarn = console.warn
console.warn = (...args) => {
  const line = args.map(String).join(" ")
  warnings.push(line)
  originalWarn(...args)
}

// Use the installed converter's public standalone-footprint lifecycle. The
// authoritative source text is the only geometry input.
const converter = new KicadFootprintToCircuitJsonConverter()
converter.addFile("SW_MX_HE_0deg_1u.kicad_mod", source)
converter.runUntilFinished()
const converted = converter.getOutput()
console.warn = originalWarn
if (typeof converter.getWarnings === "function") {
  const converterWarnings = converter.getWarnings()
  if (Array.isArray(converterWarnings)) warnings.push(...converterWarnings.map(String))
}
if (typeof converter.getStats === "function") stats = converter.getStats()

fs.writeFileSync(
  path.join(evidenceDir, "converter-api.json"),
  `${JSON.stringify({
    package: "kicad-to-circuit-json",
    version: converterVersion,
    resolvedEntry: path.relative(root, converterEntry),
    export: "KicadFootprintToCircuitJsonConverter",
    constructorArity: KicadFootprintToCircuitJsonConverter.length,
    prototypeMethods: Object.getOwnPropertyNames(KicadFootprintToCircuitJsonConverter.prototype),
  }, null, 2)}\n`,
)

const elements = Array.isArray(converted)
  ? converted
  : Array.isArray(converted?.circuitJson)
    ? converted.circuitJson
  : Array.isArray(converted?.circuit_json)
    ? converted.circuit_json
    : Array.isArray(converted?.elements)
      ? converted.elements
      : []

fs.writeFileSync(
  path.join(evidenceDir, "SW_MX_HE_0deg_1u.circuit.json"),
  `${JSON.stringify(converted, null, 2)}\n`,
)
fs.writeFileSync(
  path.join(evidenceDir, "converter-warnings.txt"),
  warnings.length ? `${warnings.join("\n")}\n` : "(none)\n",
)
fs.writeFileSync(
  path.join(evidenceDir, "converter-stats.json"),
  `${JSON.stringify(stats, null, 2)}\n`,
)

const approx = (a, b) =>
  typeof a === "number" && typeof b === "number" && Math.abs(a - b) < 1e-6
const typeOf = (e) => String(e?.type ?? "")
const xy = (e) => ({ x: e?.x ?? e?.center?.x, y: e?.y ?? e?.center?.y })
const size = (e) => ({
  x: e?.width ?? e?.size?.x ?? e?.outer_width,
  y: e?.height ?? e?.size?.y ?? e?.outer_height,
})
const numberOf = (e) =>
  String(e?.pin_number ?? e?.pad_number ?? e?.port_hints?.[0] ?? "")
const matchingPosition = (items, expected) =>
  items.find((e) => approx(xy(e).x, expected.x) && approx(Math.abs(xy(e).y), Math.abs(expected.y)))

const smd = elements.filter((e) => /smtpad/i.test(typeOf(e)))
const plated = elements.filter((e) => /plated.*hole/i.test(typeOf(e)))
const holes = elements.filter((e) => /hole/i.test(typeOf(e)) && !/plated/i.test(typeOf(e)))
const keepouts = elements.filter((e) => /keepout/i.test(typeOf(e)))

const expectedSmd = [
  { number: "1", x: -0.9375, y: -0.95, width: 1.475, height: 0.6 },
  { number: "2", x: -0.9375, y: 0.95, width: 1.475, height: 0.6 },
  { number: "3", x: 0.9375, y: 0, width: 1.475, height: 0.6 },
]
const sourceAssertions = {
  authoritativePads: [
    '(pad "1" smd roundrect\n\t\t(at -0.9375 -0.95)',
    '(pad "2" smd roundrect\n\t\t(at -0.9375 0.95)',
    '(pad "3" smd roundrect\n\t\t(at 0.9375 0)',
    '(pad "3" thru_hole circle\n\t\t(at 2.3 0)',
    '(pad "" np_thru_hole circle\n\t\t(at -5.08 0)',
    '(pad "" np_thru_hole circle\n\t\t(at 5.08 0)',
  ].every((fragment) => source.includes(fragment)),
  keepoutCount: (source.match(/\(zone\n/g) ?? []).length,
  copperPourOnlyForbidden: (source.match(/\(copperpour not_allowed\)/g) ?? []).length === 2,
}
if (!sourceAssertions.authoritativePads || sourceAssertions.keepoutCount !== 2 || !sourceAssertions.copperPourOnlyForbidden) {
  throw new Error(`authoritative footprint no longer matches the STOP 1 fixture: ${JSON.stringify(sourceAssertions)}`)
}
const smdChecks = expectedSmd.map((expected) => {
  const item = smd.find((e) => numberOf(e) === expected.number && matchingPosition([e], expected))
  return {
    expected,
    preserved: Boolean(item && approx(size(item).x, expected.width) && approx(size(item).y, expected.height)),
    observed: item ?? null,
  }
})
const thExpected = { number: "3", x: 2.3, y: 0, drill: 0.3, size: 0.6 }
const th = plated.find((e) => numberOf(e) === "3" && matchingPosition([e], thExpected))
const thDrill = th?.hole_diameter ?? th?.drill_diameter
const thSize = th?.outer_diameter ?? th?.diameter ?? size(th).x
const thPreserved = Boolean(th && approx(thDrill, thExpected.drill) && approx(thSize, thExpected.size))
const npthChecks = [-5.08, 5.08].map((x) => {
  const item = holes.find((e) => matchingPosition([e], { x, y: 0 }))
  const drill = item?.hole_diameter ?? item?.drill_diameter ?? item?.diameter
  return { expected: { x, y: 0, drill: 1.7 }, preserved: Boolean(item && approx(drill, 1.7)), observed: item ?? null }
})

const allLocated = [...smdChecks, ...npthChecks].every((c) => c.observed) && Boolean(th)
const yModes = smdChecks
  .filter((c) => c.observed && c.expected.y !== 0)
  .map((c) => (approx(xy(c.observed).y, c.expected.y) ? "identity" : "y-inverted"))
const coordinateTransform = allLocated && new Set(yModes).size <= 1
  ? (yModes[0] ?? "identity")
  : "unverifiable"

// Circuit JSON must expose both layer scope and the four KiCad keepout
// permissions. Merely finding polygon coordinates is insufficient.
const keepoutSemanticFields = ["tracks", "vias", "pads", "footprints", "copperpour"]
const semanticKeepouts = keepouts.filter((e) => {
  const flattened = JSON.stringify(e).toLowerCase().replaceAll("_", "")
  return keepoutSemanticFields.every((field) => flattened.includes(field))
})
const frontKeepout = semanticKeepouts.some((e) => /F\.Cu/i.test(JSON.stringify(e)))
const backInternalKeepout = semanticKeepouts.some((e) => {
  const serialized = JSON.stringify(e)
  return /B\.Cu/i.test(serialized) && /In1\.Cu/i.test(serialized) && /In30\.Cu/i.test(serialized)
})
const keepoutsPreserved = semanticKeepouts.length >= 2 && frontKeepout && backInternalKeepout

const status = {
  smdPads: smdChecks.every((c) => c.preserved) ? "preserved" : smdChecks.some((c) => c.observed) ? "transformed" : "lost",
  throughHolePad3: thPreserved ? "preserved" : th ? "transformed" : "lost",
  duplicatePad3: th && smd.some((e) => numberOf(e) === "3") ? "preserved" : "lost",
  npth: npthChecks.every((c) => c.preserved) && holes.length >= 2 ? "preserved" : holes.length ? "transformed" : "lost",
  platedVsNonPlated: th && npthChecks.every((c) => c.observed) ? "preserved" : "unverifiable",
  alignment: coordinateTransform === "unverifiable" ? "unverifiable" : coordinateTransform === "identity" ? "preserved" : "transformed",
  keepouts: keepoutsPreserved ? "preserved" : keepouts.length ? "unverifiable" : "lost",
}
const stop1 = Object.values(status).some((value) => value === "lost" || value === "unverifiable")
const report = {
  input: path.relative(root, inputPath),
  converter: { package: "kicad-to-circuit-json", version: converterVersion, api: "KicadFootprintToCircuitJsonConverter" },
  sourceAssertions,
  outputElementCount: elements.length,
  coordinateTransform,
  footprintPlacement: { origin: { x: 0, y: 0 }, rotationDegrees: 0 },
  status,
  checks: { smd: smdChecks, throughHolePad3: th ?? null, npth: npthChecks, keepouts },
  warnings,
  stats,
  result: stop1 ? "STOP 1 — FOOTPRINT INTEGRITY" : "PASS candidate",
}
fs.writeFileSync(path.join(evidenceDir, "geometry-verification-report.json"), `${JSON.stringify(report, null, 2)}\n`)
fs.writeFileSync(
  path.join(evidenceDir, "verification-result.json"),
  `${JSON.stringify({ stop1, result: report.result, status }, null, 2)}\n`,
)
console.log(JSON.stringify(report, null, 2))

// Conversion/execution exceptions fail this process before a result is
// produced. CI evaluates a successfully produced STOP 1 result separately.
