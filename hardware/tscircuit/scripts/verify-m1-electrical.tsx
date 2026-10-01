import assert from "node:assert/strict"
import { mkdir, readFile, writeFile } from "node:fs/promises"
import path from "node:path"
import React from "react"
import { Circuit } from "@tscircuit/core"
import { M1FourKeyElectrical } from "../src/evaluation/m1-four-key"

type E = Record<string, any>
const out = path.resolve("tscircuit-m1-electrical")
const circuit = new Circuit()
circuit.add(<M1FourKeyElectrical />)
await circuit.renderUntilSettled()
const json = circuit.getCircuitJson() as E[]
const pinmap = await readFile(path.resolve("../sensor-test/pinmap.csv"), "utf8")
await mkdir(out, { recursive: true })
await writeFile(path.join(out, "circuit.json"), JSON.stringify(json, null, 2) + "\n")
const of = (type: string) => json.filter(x => x.type === type)
const components = of("source_component"), ports = of("source_port"), nets = of("source_net"), traces = of("source_trace")
const component = (name: string) => { const m=components.filter(x=>x.name===name); assert.equal(m.length,1,`${name} count`); return m[0] }
const port = (c:E,name:string) => { const m=ports.filter(x=>x.source_component_id===c.source_component_id&&x.name===name); assert.equal(m.length,1,`${c.name}.${name}`); return m[0] }
const net = (name:string) => { const m=nets.filter(x=>x.name===name); assert.equal(m.length,1,`${name} net`); return m[0] }
const connected = (cname:string,pname:string,nname:string) => {
  const p=port(component(cname),pname), n=net(nname)
  assert.ok(traces.some(t=>t.connected_source_port_ids?.includes(p.source_port_id)&&t.connected_source_net_ids?.includes(n.source_net_id)),`${cname}.${pname} -> ${nname}`)
}
const categories:Record<string,string>={}
const check=(name:string,fn:()=>string)=>{try{categories[name]=`PASS: ${fn()}`}catch(e){categories[name]=`FAIL: ${e instanceof Error?e.message:e}`};console.log(`${name}: ${categories[name]}`)}
check("componentCounts",()=>{for(const [prefix,count] of [["U_H",4],["U_MUX",1],["U_MCU",1],["J_USB",1],["U_FLASH",1],["Y1",1],["U_LDO",1],["U_LOAD",1]] as const) assert.equal(components.filter(x=>x.name.startsWith(prefix)).length,count,`${prefix} count`);return "four Hall sensors and every required active block present"})
check("requiredNets",()=>{for(const n of ["HALL_5V","V3V3","USB_DP","USB_DM","H0_RAW","H1_RAW","H2_RAW","H3_RAW","MUX_D","ADC0_FILTERED","HALL_PWR_EN","MUX_A0","MUX_A1","MUX_A2","MUX_EN0","SWDIO","SWCLK","RUN"]) net(n);return "all required source nets are unique"})
check("hallTopology",()=>{for(let i=0;i<4;i++){connected(`U_H${i}`,"VCC","HALL_5V");connected(`U_H${i}`,"OUT",`H${i}_RAW`);connected("U_MUX",`S${i+1}`,`H${i}_RAW`)}connected("U_LOAD","OUT","HALL_5V");connected("U_MUX","VDD","HALL_5V");return "load switch, four Hall sensors, and TMUX S1-S4 resolve through source ports/traces/nets"})
check("logicAndUsb",()=>{for(const n of ["USB_DP","USB_DM","HALL_PWR_EN","MUX_A0","MUX_A1","MUX_A2","MUX_EN0","SWDIO","SWCLK","RUN"]) connected("U_MCU",n,n);connected("U_LDO","VOUT","V3V3");connected("U_MCU","IOVDD","V3V3");return "USB, 3V3, controls, reset and SWD resolve at RP2040"})
check("adcInterface",()=>{connected("U_MUX","D","MUX_D");connected("R_ADC_TOP","pin1","MUX_D");connected("R_ADC_TOP","pin2","ADC0_FILTERED");connected("R_ADC_BOTTOM","pin1","ADC0_FILTERED");connected("C_ADC","pin1","ADC0_FILTERED");connected("U_MCU","ADC0_FILTERED","ADC0_FILTERED");assert.equal(component("R_ADC_TOP").resistance,6800);assert.equal(component("R_ADC_BOTTOM").resistance,10000);assert.equal(component("C_ADC").capacitance,1e-9);return "MUX_D -> 6.8k/10k/1nF -> RP2040 ADC0"})
check("decoupling",()=>{for(const [c,n] of [["C_MUX","HALL_5V"],["C_HALL0","HALL_5V"],["C_HALL1","HALL_5V"],["C_HALL2","HALL_5V"],["C_HALL3","HALL_5V"],["C_MCU_IO","V3V3"],["C_MCU_CORE","V1V1"],["C_FLASH","V3V3"],["C_LDO_IN","VBUS"],["C_LDO_OUT","V3V3"]]){connected(c,"pin1",n);connected(c,"pin2","GND")}return "required local decoupling resolves between its supply and GND"})
check("testPoints",()=>{for(const n of ["VBUS","V3V3","HALL_5V","H0_RAW","H1_RAW","H2_RAW","H3_RAW","MUX_D","ADC0_FILTERED","GND","SWDIO","SWCLK"]) connected(`TP_${n}`,"pin1",n);return "all required measurement pads resolve to their source nets"})
check("partIdentity",()=>{const ids:Record<string,[string,string]>={U_MCU:["RP2040","C2040"],U_LDO:["AP2112K-3.3TRG1","C51118"],U_LOAD:["TPS22919DCKR","C2149796"],U_MUX:["TMUX1208PWR","C494728"],J_USB:["TYPE-C-31-M-12","C165948"],U_H0:["DRV5055A3QDBZR","C266128"]};for(const [ref,[mpn,jlc]] of Object.entries(ids)){const c=component(ref);assert.equal(c.manufacturer_part_number,mpn);assert.ok(c.supplier_part_numbers?.jlcpcb?.includes(jlc))}return "all six approved MPN/JLCPCB identities retained"})
check("pinmap",()=>{for(const [signal,pin] of Object.entries({MUX_A0:"GPIO2",MUX_A1:"GPIO3",MUX_A2:"GPIO4",MUX_EN0:"GPIO5",HALL_PWR_EN:"GPIO7",STATUS_LED:"GPIO11",ADC_A:"GPIO26/ADC0",USB_DP:"USB_DP",USB_DM:"USB_DM",SWDIO:"SWDIO",SWCLK:"SWCLK",RUN:"RUN"}))assert.ok(pinmap.includes(`${signal},${pin},`),`${signal} ${pin}`);return "RP2040 assignments match pinmap.csv"})
const electricalErrors=json.filter(x=>["source_failed_to_create_component_error","source_trace_not_connected_error","source_pin_must_be_connected_error","pcb_missing_footprint_error"].includes(x.type))
check("electricalErrors",()=>{assert.equal(electricalErrors.length,0,JSON.stringify(electricalErrors));return "missing-footprint count 0; electrical error count 0"})
check("usbGeometry",()=>{const c=component("J_USB"),pcb=of("pcb_component").find(x=>x.source_component_id===c.source_component_id),pads=of("pcb_smtpad").filter(x=>x.pcb_component_id===pcb?.pcb_component_id),holes=of("pcb_plated_hole").filter(x=>x.pcb_component_id===pcb?.pcb_component_id);assert.equal(pads.length,16);assert.equal(holes.length,2);for(const p of pads){assert.deepEqual([p.width,p.height].sort((a,b)=>a-b),[0.3,1.15])}assert.deepEqual(holes.map(x=>x.hole_diameter),[0.65,0.65]);return "TYPE-C-31-M-12 has 16 contacts and two 0.65mm shell holes"})
const failed=Object.values(categories).filter(x=>x.startsWith("FAIL"))
await writeFile(path.join(out,"verification-result.json"),JSON.stringify({result:failed.length?"FAIL":"PASS",categories,component_count:components.length,missing_footprint_count:of("pcb_missing_footprint_error").length,electrical_error_count:electricalErrors.length,design_data_gaps:["passive supplier part numbers","LED supplier part numbers","buttons/test points supplier part numbers"]},null,2)+"\n")
if(failed.length)process.exitCode=1
