// Replay unchanged stock checks on a clone; never write generated circuit data.
import fs from 'node:fs'
import path from 'node:path'
import {createHash} from 'node:crypto'
import {pathToFileURL} from 'node:url'
const [environment, run] = process.argv.slice(2)
const {runAllPlacementChecks,runAllRoutingChecks} = await import(pathToFileURL(path.resolve(environment,'node_modules/@tscircuit/checks/dist/index.js')))
const raw = fs.readFileSync(run+'/circuit.json')
const records = [...await runAllPlacementChecks(JSON.parse(raw)), ...await runAllRoutingChecks(JSON.parse(raw))].filter(e=>e.type.endsWith('_error'))
fs.mkdirSync(run+'/evidence',{recursive:true})
fs.writeFileSync(run+'/evidence/stock-check-records.json',JSON.stringify({input_sha256:createHash('sha256').update(raw).digest('hex'),records},null,2)+'\n')
