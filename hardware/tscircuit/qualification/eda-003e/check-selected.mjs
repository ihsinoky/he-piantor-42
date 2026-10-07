// Replay stock via checker only for the retained signature; never rewrite geometry.
import fs from 'node:fs'
import {gunzipSync} from 'node:zlib'
import assert from 'node:assert/strict'
import {checkViaTraceClearance} from '../eda-003c/latest-stock/node_modules/@tscircuit/checks/dist/index.js'
const here=new URL('./',import.meta.url)
const population=JSON.parse(fs.readFileSync(new URL('evidence/signature-population.json',here)))
const accepted=JSON.parse(gunzipSync(fs.readFileSync(new URL('../eda-003c/evidence/raw/latest-main.circuit.json.gz',here))))
for(const [label,circuit] of [['accepted',accepted],['isolated_capture',JSON.parse(fs.readFileSync(process.argv[2]))]]){
 const errors=checkViaTraceClearance(structuredClone(circuit))
 for(const r of population.records){
  const error=errors.find(e=>e.pcb_via_id===r.via_id&&e.pcb_trace_id===r.pcb_trace_id)
  assert(error,`${label}: missing ${r.record_id}`)
  assert.equal(error.minimum_clearance,.2)
  assert(Math.abs(error.actual_clearance-r.material_spacing_mm)<1e-10)
 }
 console.log(`PASS ${label}: 15 selected stock checker rejections at unmodified .20 mm`)
}
