import assert from "node:assert/strict"
import { mkdir, writeFile } from "node:fs/promises"
import path from "node:path"
import React from "react"
import { Circuit } from "@tscircuit/core"
import { CheckpointCBoard } from "../src/spikes/native-hall/checkpoint-c"

type Element = Record<string, any>
const output = path.resolve("tscircuit-native-checkpoint-c")
const circuit = new Circuit()
circuit.add(<CheckpointCBoard />)
await circuit.renderUntilSettled()
const json = circuit.getCircuitJson() as Element[]
const ofType = (type: string) => json.filter((item) => item.type === type)
const checks: Record<string, string> = {}
const check = (name: string, fn: () => string) => {
  try { checks[name] = `PASS: ${fn()}` } catch (error) { checks[name] = `FAIL: ${error instanceof Error ? error.message : error}` }
  console.log(`${name}: ${checks[name]}`)
}

const board = ofType("pcb_board")[0]
const source = (name: string) => json.find((item) => item.type === "source_component" && item.name === name)
const pcbFor = (name: string) => ofType("pcb_component").find((item) => item.source_component_id === source(name)?.source_component_id)
check("boardTwoLayers", () => { assert.equal(ofType("pcb_board").length, 1); assert.equal(board.num_layers, 2); return "one board, num_layers=2" })
check("boardThickness", () => { assert.equal(board.thickness, 1.2); return "1.2mm" })
check("boardOutline", () => { assert.ok((board.outline?.length ?? 0) >= 4 || (board.width > 0 && board.height > 0)); return "board outline present" })
check("components", () => { for (const name of ["U1", "C_HALL1", "TP_H0_RAW"]) assert.ok(pcbFor(name), `${name} missing`); return "U1, C_HALL1, TP_H0_RAW represented" })
check("geometry", () => { assert.equal(ofType("pcb_smtpad").filter((x) => x.pcb_component_id === pcbFor("U1")?.pcb_component_id).length, 3); assert.equal(ofType("pcb_plated_hole").length, 1); assert.equal(ofType("pcb_hole").length, 2); return "Hall 3 SMD, 1 PTH, 2 NPTH" })
check("keepoutsPreserved", () => { assert.ok(ofType("pcb_keepout").length >= 2); return `${ofType("pcb_keepout").length} keepouts` })
check("routingGenerated", () => { assert.ok(ofType("pcb_trace").length > 0); return `${ofType("pcb_trace").length} PCB traces` })
check("viaGenerated", () => { const via = ofType("pcb_via").find((x) => x.source_net_id === json.find((item) => item.type === "source_net" && item.name === "GND")?.source_net_id); assert.ok(via); assert.deepEqual(via.layers, ["top", "bottom"]); assert.equal(via.from_layer, "top"); assert.equal(via.to_layer, "bottom"); assert.equal(via.hole_diameter, .3); assert.equal(via.outer_diameter, .6); return "0.30/0.60mm top-bottom GND via" })
check("topCopperPour", () => { assert.ok(ofType("pcb_copper_pour").some((x) => x.layer === "top")); return "present" })
check("bottomCopperPour", () => { assert.ok(ofType("pcb_copper_pour").some((x) => x.layer === "bottom")); return "present" })
const errors = json.filter((item) => item.type.endsWith("_error"))
check("circuitJsonErrors", () => { assert.equal(errors.length, 0, JSON.stringify(errors)); return "0" })

const failed = Object.entries(checks).filter(([, value]) => value.startsWith("FAIL"))
const summary = { board_layer_count: board?.num_layers, board_thickness_mm: board?.thickness, pcb_trace_count: ofType("pcb_trace").length, pcb_via_count: ofType("pcb_via").length, pcb_keepout_count: ofType("pcb_keepout").length, circuit_json_error_count: errors.length }
await mkdir(output, { recursive: true })
await writeFile(path.join(output, "circuit.json"), `${JSON.stringify(json, null, 2)}\n`)
await writeFile(path.join(output, "pcb-verification-result.json"), `${JSON.stringify({ checkpoint: "C", result: failed.length ? "FAIL" : "PASS", categories: checks, errors }, null, 2)}\n`)
await writeFile(path.join(output, "pcb-summary.json"), `${JSON.stringify(summary, null, 2)}\n`)
if (failed.length) process.exitCode = 1
