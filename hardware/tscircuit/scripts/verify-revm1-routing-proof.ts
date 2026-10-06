import { readFile, writeFile } from "node:fs/promises"
import { createHash } from "node:crypto"
import { runAllPlacementChecks, runAllRoutingChecks } from "@tscircuit/checks"
import { verifyPhysical, type E } from "./revm1-physical-connectivity"

const [input,output]=process.argv.slice(2)
if(!input||!output)throw new Error("Usage: bun verify-revm1-routing-proof.ts CIRCUIT_JSON SUMMARY_JSON")
const raw=await readFile(input), json=JSON.parse(raw.toString()) as E[]
const connectivity=verifyPhysical(json)
// Stock runAllRoutingChecks annotates its array. Clone isolates all changes;
// untouched disk bytes are hashed again after checking. No repairs are saved.
const clone=structuredClone(json)
const generated=json.filter(e=>e.type.endsWith("_error")||e.type.endsWith("_warning"))
// runAllPlacementChecks includes copper/keepout, board-edge and via-in-pad
// validation. Do not append it again and double-count the same violation.
const checked=[...await runAllPlacementChecks(clone),...await runAllRoutingChecks(clone)] as E[]
const counts=(es:E[])=>Object.fromEntries([...new Set(es.map(x=>x.type))].sort().map(t=>[t,es.filter(x=>x.type===t).length]))
const board=json.find(x=>x.type==="pcb_board")
const boardValid=json.filter(x=>x.type==="pcb_board").length===1&&board?.num_layers===2&&board?.thickness===1.2&&board?.width>0&&board?.height>0
const materialErrors=checked.filter(x=>x.type.endsWith("_error")||x.type==="pcb_keepout_overlap_warning")
const sourceHash=createHash("sha256").update(raw).digest("hex")
if(sourceHash!==createHash("sha256").update(await readFile(input)).digest("hex"))throw new Error("Verifier mutated the generated file")
const summary={...connectivity,board:{width_mm:board?.width,height_mm:board?.height,layers:board?.num_layers,thickness_mm:board?.thickness,valid:boardValid},
  raw_sha256:sourceHash,generated_diagnostic_counts:counts(generated),stock_check_counts:counts(checked),
  generated_diagnostics:generated.map(x=>({type:x.type,message:x.message})),
  stock_material_diagnostics:materialErrors.map(x=>({type:x.type,message:x.message})),
  result:boardValid&&connectivity.complete&&!generated.some(x=>x.type.endsWith("_error"))&&!materialErrors.length?"PASS":"FAIL"}
await writeFile(output,JSON.stringify(summary,null,2)+"\n")
console.log(JSON.stringify({result:summary.result,unrouted:summary.electrically_required_unrouted_count,traces:summary.routed_trace_count,vias:summary.via_count,
  generated:summary.generated_diagnostic_counts,checked:summary.stock_check_counts,shorts:summary.wrong_net_copper_components.length}))
if(summary.result!=="PASS")process.exitCode=1
