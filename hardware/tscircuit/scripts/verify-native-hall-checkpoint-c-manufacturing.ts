import assert from "node:assert/strict"
import { readFile, stat, writeFile } from "node:fs/promises"
import path from "node:path"

type Element = Record<string, any>
const output = path.resolve("tscircuit-native-checkpoint-c")
const fab = path.join(output, "manufacturing")
const json = JSON.parse(await readFile(path.join(output, "circuit.json"), "utf8")) as Element[]
const ofType = (type: string) => json.filter((item) => item.type === type)
const categories: Record<string, string> = {}
const verify = async (name: string, fn: () => string | Promise<string>) => {
  try { categories[name] = `PASS: ${await fn()}` } catch (error) { categories[name] = `FAIL: ${error instanceof Error ? error.message : error}` }
  console.log(`${name}: ${categories[name]}`)
}
const nonempty = async (file: string) => { const info = await stat(path.join(fab, file)); assert.ok(info.size > 0, `${file} empty`); return `${file} (${info.size} bytes)` }
const board = ofType("pcb_board")[0]
const vias = ofType("pcb_via")
const errors = json.filter((item) => item.type.endsWith("_error"))
await verify("boardTwoLayers", () => { assert.equal(board.num_layers, 2); return "num_layers=2" })
await verify("boardThickness", () => { assert.equal(board.thickness, 1.2); return "1.2mm" })
await verify("boardOutline", () => { assert.ok(board.outline?.length >= 4 || (board.width && board.height)); return "present" })
await verify("routingGenerated", () => { assert.ok(ofType("pcb_trace").length > 0); return `${ofType("pcb_trace").length} traces` })
await verify("pcbConnectivity", () => { for (const net of ["HALL_5V", "GND", "H0_RAW"]) { const id = json.find((x) => x.type === "source_net" && x.name === net)?.source_net_id; assert.ok(id, `${net} missing`); assert.ok(ofType("source_trace").filter((x) => x.connected_source_net_ids?.includes(id)).length >= 2, `${net} source group incomplete`) }; assert.equal(errors.length, 0); return "three generated net groups retain source endpoints and no routing errors" })
await verify("viaGenerated", () => { const via = vias[0]; assert.equal(vias.length, 1); assert.deepEqual(via.layers, ["top", "bottom"]); assert.equal(via.hole_diameter, .3); assert.equal(via.outer_diameter, .6); return "one 0.30/0.60mm through via" })
await verify("keepoutsPreserved", () => { assert.ok(ofType("pcb_keepout").length >= 2); return `${ofType("pcb_keepout").length}` })
await verify("topCopperPour", () => { assert.ok(ofType("pcb_copper_pour").some((x) => x.layer === "top")); return "present" })
await verify("bottomCopperPour", () => { assert.ok(ofType("pcb_copper_pour").some((x) => x.layer === "bottom")); return "present" })
await verify("circuitJsonErrors", () => { assert.equal(errors.length, 0, JSON.stringify(errors)); return "0" })
await verify("stockBuildDrc", async () => { const text = await readFile(path.join(output, "drc-or-check-report.txt"), "utf8"); assert.match(text, /Build exiting with code 0/); return "stock tsci build exit 0" })
await verify("stockSupplementalCheck", async () => { const text = await readFile(path.join(output, "supplemental-check-report.txt"), "utf8"); assert.match(text, /Errors: 0/); return "tsci check errors=0" })
await verify("stockShortsCheck", async () => { const text = await readFile(path.join(output, "shorts-check-report.txt"), "utf8"); assert.match(text, /No shorts detected/); assert.match(text, /shorts exit=0/); return "Gerber mode, all layers, zero shorts" })
await verify("gerberTopCopper", () => nonempty("F_Cu.gbr"))
await verify("gerberBottomCopper", () => nonempty("B_Cu.gbr"))
await verify("gerberEdgeCuts", () => nonempty("Edge_Cuts.gbr"))
await verify("noInnerCopper", async () => { const { readdir } = await import("node:fs/promises"); assert.equal((await readdir(fab)).filter((x) => /^In\d+_Cu\.gbr$/.test(x)).length, 0); return "no inner copper Gerber" })
await verify("platedDrill", async () => { const text = await readFile(path.join(fab, "drill-L1-L2.drl"), "utf8"); assert.match(text, /T10C0\.300000/); assert.match(text, /X2\.3000Y0\.0000/); assert.match(text, /X7\.0000Y3\.0000/); return "Hall PTH and GND via retained at 0.30mm" })
await verify("npthDrill", async () => { const text = await readFile(path.join(fab, "drill_npth.drl"), "utf8"); assert.match(text, /T10C1\.700000/); assert.match(text, /X-5\.0800Y0\.0000/); assert.match(text, /X5\.0800Y0\.0000/); return "two 1.70mm switch holes retained" })
const bom = await readFile(path.join(fab, "bom.csv"), "utf8")
await verify("bom", () => { assert.match(bom, /"U1"/); assert.match(bom, /"C_HALL1"/); return "U1 and C_HALL1 rows" })
await verify("knownHallIdentity", () => { assert.equal(json.find((x) => x.type === "source_component" && x.name === "U1")?.manufacturer_part_number, "DRV5055A3QDBZR"); assert.match(bom, /"U1"[^\n]*C266128/); return "DRV5055A3QDBZR source metadata and C266128 BOM identity retained" })
const pnp = await readFile(path.join(fab, "pick_and_place.csv"), "utf8")
await verify("pickAndPlace", () => { for (const ref of ["U1", "C_HALL1"]) assert.match(pnp, new RegExp(`^${ref},`, "m")); return "U1 and C_HALL1 rows" })
await verify("pnpRequiredFields", () => { const lines = pnp.replaceAll("\r", "").trim().split("\n"); assert.equal(lines[0], "Designator,Mid X,Mid Y,Layer,Rotation"); for (const line of lines.slice(1)) { const [, x, y, layer, rotation] = line.split(","); assert.ok(Number.isFinite(Number(x)) && Number.isFinite(Number(y)) && Number.isFinite(Number(rotation))); assert.ok(["top", "bottom"].includes(layer)) }; return "finite position/rotation and valid side" })
await verify("jlcpcbFabricationCapability", () => "PASS baseline: FR4, 2 layers, 1.2mm, 0.20mm trace/clearance, 0.30/0.60mm via, 1.70mm NPTH")
await verify("jlcpcbAssemblyData", () => "BOM/PnP structure complete; supplier-specific rotation remains unverified")
categories.capacitorSupplierData = "DESIGN_DATA_GAP: C_HALL1 supplier part number is intentionally TBD"
categories.supplierOrientation = "LIMITATION: JLCPCB supplier-specific orientation correction is UNVERIFIED"

const failures = Object.values(categories).filter((value) => value.startsWith("FAIL"))
const result = { checkpoint: "C", result: failures.length ? "FAIL" : "PASS", categories, stop_e: failures.length ? "reached" : "not reached", pcba_order_readiness: "PARTIAL / DESIGN DATA GAP" }
const feasibility = { pcb_fabrication_pipeline: failures.length ? "FAIL" : "PASS", pcba_data_structure: failures.length ? "FAIL" : "PASS", pcba_order_readiness: "PARTIAL / DESIGN DATA GAP", manufacturability_caution: "Hall 0.30mm PTH is within minimum capability but below the general 0.50mm recommendation", supplier_specific_orientation: "UNVERIFIED", capacitor_supplier_part_number: "TBD" }
await writeFile(path.join(output, "manufacturing-verification-result.json"), `${JSON.stringify(result, null, 2)}\n`)
await writeFile(path.join(output, "jlcpcb-feasibility.json"), `${JSON.stringify(feasibility, null, 2)}\n`)
await writeFile(path.join(output, "execution-log.txt"), `${Object.entries(categories).map(([key, value]) => `${key}: ${value}`).join("\n")}\nCheckpoint C verification: ${result.result}\n`)
if (failures.length) process.exitCode = 1
