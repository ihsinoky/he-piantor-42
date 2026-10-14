import React from "react"
import { Circuit } from "tscircuit"
import { RepresentativeMain } from "./src/qualification/revm1-routing-proof"
import { writeFileSync } from "node:fs"
import { createHash } from "node:crypto"
const circuit = new Circuit()
circuit.add(<RepresentativeMain strategy={3}/> )
await circuit.renderUntilSettled()
const raw = JSON.stringify(circuit.getCircuitJson(), null, 2) + "\n"
writeFileSync(process.argv[2], raw)
console.log(JSON.stringify({raw_saved:true,sha256:createHash("sha256").update(raw).digest("hex"),routingDisabled:true,source_strategy:3}))
