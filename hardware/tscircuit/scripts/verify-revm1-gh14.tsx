import assert from "node:assert/strict"
import { createHash } from "node:crypto"
import { readFile, writeFile } from "node:fs/promises"
import React from "react"
import { Circuit } from "@tscircuit/core"
import { JstGh14 } from "../src/qualification/JstGh14"

// Independent oracle transcribed from PO drawing KRD-32980-5 R0, page 2.
// Values are not imported from footprint constants or generated data.
const expectedX=[8.125,6.875,5.625,4.375,3.125,1.875,.625,-.625,-1.875,-3.125,-4.375,-5.625,-6.875,-8.125]
const digest="1707350a5780a7c8a7b95e67430cc0b8ddda36ebe1a6fb04d6ab4cfc536776d1"
const pdf=await readFile(new URL("../../../BM14B-GHS-TBT.pdf",import.meta.url))
assert.equal(createHash("sha256").update(pdf).digest("hex"),digest)
const c=new Circuit(); c.add(<board width={30} height={15} routingDisabled schematicDisabled><JstGh14 name="J1"/></board>)
await c.renderUntilSettled()
const json=c.getCircuitJson() as Record<string,any>[]
const pads=json.filter(x=>x.type==="pcb_smtpad")
const close=(a:number,b:number)=>assert.ok(Number.isFinite(a)&&Math.abs(a-b)<.001,`${a} != ${b}`)
assert.equal(pads.length,16)
for(let i=0;i<14;i++){
  const p=pads.find(x=>x.port_hints?.includes(`pin${i+1}`)); assert.ok(p)
  close(p.x,expectedX[i]);close(p.y,0);close(p.width,.6);close(p.height,1.7);assert.equal(p.layer,"top")
}
const mp=pads.filter(x=>x.port_hints?.includes("MP"));assert.equal(mp.length,2)
for(const p of mp){close(Math.abs(p.x),9.975);close(p.y,-3.35);close(p.width,1);close(p.height,2.8)}
assert.ok(json.some(x=>x.type==="pcb_silkscreen_text"&&x.text==="1"))
const body=json.find(x=>x.type==="pcb_silkscreen_rect");assert.ok(body)
close(body.width,20.75);close(body.height,4.25);close(body.center.x,0);close(body.center.y,-2.325)
const mark=json.find(x=>x.type==="pcb_silkscreen_text"&&x.text==="1")!
close(mark.anchor_position.x,8.125);close(mark.anchor_position.y,1.7)
const errors=json.filter(x=>x.type.endsWith("_error"));assert.equal(errors.length,0,JSON.stringify(errors))
const result={result:"PASS",manufacturer_pdf_sha256:digest,drawing:"KRD-32980-5 R0, 2024-03-13, page 2",
  tolerance_mm:.001,contact_count:14,pitch_mm:1.25,span_mm:16.25,signal_lands_mm:[.6,1.7],
  reinforcement_lands:{count:2,size_mm:[1,2.8],centers_mm:[[-9.975,-3.35],[9.975,-3.35]]},
  body:{A_mm:16.25,B_mm:20.75,depth_mm:4.25,height_above_standoff_mm:4.05,standoff_mm:.15},
  origin:"signal row midpoint; +x right/+y up; pin 1 at +8.125,0",
  catalogue_comparison:"CONSISTENT",prior_record_comparison:"CONSISTENT",prerequisite:"RESOLVED"}
if(process.argv[2]) await writeFile(process.argv[2],JSON.stringify(result,null,2)+"\n")
console.log(JSON.stringify(result))
