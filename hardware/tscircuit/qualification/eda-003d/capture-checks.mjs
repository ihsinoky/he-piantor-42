// Read-only replay of accepted stock checks; no circuit generation or routing.
import { readFileSync, writeFileSync } from 'node:fs'
import { gunzipSync } from 'node:zlib'
import { createHash } from 'node:crypto'
import { fileURLToPath } from 'node:url'
import assert from 'node:assert/strict'
import { runAllPlacementChecks, runAllRoutingChecks } from '../eda-003c/latest-stock/node_modules/@tscircuit/checks/dist/index.js'
const root = fileURLToPath(new URL('./', import.meta.url))
const accepted = root + '../eda-003c/evidence/'
const raw = gunzipSync(readFileSync(accepted + 'raw/latest-main.circuit.json.gz'))
const hash = createHash('sha256').update(raw).digest('hex')
const manifest = JSON.parse(readFileSync(accepted + 'raw/artifact-manifest.json'))
assert.equal(hash, manifest['latest-main.circuit.json.gz'].uncompressed_sha256)
const json = JSON.parse(raw)
const clone = structuredClone(json)
const records = [...await runAllPlacementChecks(clone), ...await runAllRoutingChecks(clone)].filter(e => e.type.endsWith('_error'))
const baseline = JSON.parse(readFileSync(accepted + 'latest-main-summary.json'))
assert.deepEqual(records.map(({type,message}) => ({type,message})), baseline.stock_material_diagnostics)
assert.equal(records.length, 71)
assert.equal(createHash('sha256').update(gunzipSync(readFileSync(accepted + 'raw/latest-main.circuit.json.gz'))).digest('hex'), hash)
writeFileSync(root + 'evidence/stock-check-records.json', JSON.stringify({input_sha256:hash, records}, null, 2) + '\n')
console.log('PASS: all 71 accepted diagnostics reproduced; input unchanged')
