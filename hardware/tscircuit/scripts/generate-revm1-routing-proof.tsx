import { mkdir, readFile, writeFile } from "node:fs/promises"
import { createHash } from "node:crypto"
import path from "node:path"
import React from "react"
import { Circuit } from "@tscircuit/core"
import { RepresentativeMain, RepresentativeWing, type Strategy } from "../src/qualification/revm1-routing-proof"

const [board, strategyText, output]=process.argv.slice(2)
if(!["main","wing"].includes(board)||!["1","2","3"].includes(strategyText)||!output)
  throw new Error("Usage: bun generate-revm1-routing-proof.tsx main|wing 1|2|3 OUTPUT")
await mkdir(output,{recursive:true})
const production=JSON.parse(await readFile(new URL("../package.json",import.meta.url),"utf8"))
if(production.dependencies.tscircuit!=="0.0.2646")throw new Error("Qualification requires the production 0.0.2646 pin")
const sourceHashes=Object.fromEntries(await Promise.all([
  "../src/qualification/revm1-routing-proof.tsx","../src/qualification/JstGh14.tsx",
  "../src/qualification/native-support-footprints.tsx","../src/components/HallKey.tsx",
  "../package-lock.json",
].map(async p=>[p,createHash("sha256").update(await readFile(new URL(p,import.meta.url))).digest("hex")])))
const c=new Circuit(), started=Date.now(), events:any[]=[]
let lastPhase=""
for(const event of ["autorouting:start","autorouting:end","autorouting:error","solver:started"] as const)
  c.on(event,(e:any)=>{const record={event,elapsed_ms:Date.now()-started,solverName:e?.solverName,
    error:e?.error?.message??e?.error,message:e?.message}; events.push(record);console.log(JSON.stringify(record))})
c.on("autorouting:progress",(e:any)=>{if(e?.phase!==lastPhase){lastPhase=e?.phase;const r={event:"phase",phase:lastPhase,elapsed_ms:Date.now()-started};events.push(r);console.log(JSON.stringify(r))}})
c.add(board==="main"?<RepresentativeMain strategy={Number(strategyText) as Strategy}/>:<RepresentativeWing strategy={Number(strategyText) as Strategy}/>)
let timedOut=false
const save=async()=>{
  await writeFile(path.join(output,"circuit.json"),JSON.stringify(c.getCircuitJson(),null,2)+"\n")
  await writeFile(path.join(output,"generation.json"),JSON.stringify({board,strategy:Number(strategyText),elapsed_ms:Date.now()-started,timed_out:timedOut,source_sha256:sourceHashes,events},null,2)+"\n")
}
const timer=setTimeout(async()=>{timedOut=true;await save();console.error("Bounded 300s generation deadline; partial output retained");process.exit(2)},300_000)
try{await c.renderUntilSettled();await save()}finally{clearTimeout(timer)}
console.log(`${board} strategy ${strategyText}: generated ${output}`)
