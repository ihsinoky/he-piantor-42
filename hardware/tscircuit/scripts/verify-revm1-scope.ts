import assert from "node:assert/strict"
import { readFile, writeFile } from "node:fs/promises"
import type { E } from "./revm1-physical-connectivity"

const [mainPath,wingPath,output]=process.argv.slice(2)
if(!mainPath||!wingPath||!output)throw new Error("Usage: bun verify-revm1-scope.ts MAIN_JSON WING_JSON SUMMARY")
const inspect=async(file:string,main:boolean)=>{
  const j=JSON.parse(await readFile(file,"utf8")) as E[]
  const comps=j.filter(e=>e.type==="source_component")
  const component=(name:string)=>{const c=comps.find(c=>c.name===name);assert.ok(c,`${name} missing`);return c}
  const port=(ref:string,pin:string)=>{
    const c=component(ref),p=j.find(e=>e.type==="source_port"&&e.source_component_id===c.source_component_id&&e.name===pin)
    assert.ok(p,`${ref}.${pin} missing`);return p
  }
  const connected=(ref:string,pin:string,net:string)=>{
    const p=port(ref,pin),n=j.find(e=>e.type==="source_net"&&e.name===net);assert.ok(n,`${net} missing`)
    assert.ok(j.some(e=>e.type==="source_trace"&&e.connected_source_port_ids?.includes(p.source_port_id)&&e.connected_source_net_ids?.includes(n.source_net_id)),`${ref}.${pin} not on ${net}`)
  }
  assert.equal(component("J_WING").manufacturer_part_number,"BM14B-GHS-TBT(LF)(SN)")
  // Independent accepted G0B pin table, section 2.3. All six return contacts
  // terminate on ONE source net; no split analogue/digital ground islands.
  const pinTable=["HALL_5V","GND","MUX_A0","GND","MUX_A1","MUX_A2","WING_EN","GND","MUX_OUT_A","GND","MUX_OUT_B","GND","MUX_OUT_C","GND"]
  pinTable.forEach((n,i)=>connected("J_WING",`P${i+1}`,n))
  assert.equal(j.filter(e=>e.type==="source_net"&&e.name==="GND").length,1)
  if(main){
    for(const [ref,mpn] of Object.entries({U_MCU:"RP2040",J_USB:"TYPE-C-31-M-12",U_ESD:"USBLC6-2SC6",U_FLASH:"W25Q16JVUXIQ",Y1:"ABM8-272-T3",U_LDO:"AP2112K-3.3TRG1",U_LOAD:"TPS22919DCKR"}))assert.equal(component(ref).manufacturer_part_number,mpn)
    connected("U_MCU","GND_EP","GND");connected("U_MCU","VREG_OUT","V1V1")
    connected("U_LOAD","OUT","HALL_5V");connected("U_LOAD","IN","VBUS")
    connected("R_WING_PD","pin1","WING_EN");connected("R_WING_PD","pin2","GND")
    for(const ch of ["A","B","C"]){
      connected("U_MCU",`ADC_${ch}`,`ADC_${ch}`)
      connected(`R_ADC_${ch}_TOP`,"pin1",`MUX_OUT_${ch}`);connected(`R_ADC_${ch}_TOP`,"pin2",`ADC_${ch}`)
      connected(`R_ADC_${ch}_BOTTOM`,"pin1",`ADC_${ch}`);connected(`R_ADC_${ch}_BOTTOM`,"pin2","GND")
      connected(`C_ADC_${ch}`,"pin1",`ADC_${ch}`);connected(`C_ADC_${ch}`,"pin2","GND")
    }
  }else{
    assert.equal(comps.filter(e=>e.manufacturer_part_number==="TMUX1208PWR").length,3)
    assert.equal(comps.filter(e=>e.manufacturer_part_number==="DRV5055A3QDBZR").length,4)
    for(const [ch,ids] of [["A",[0,2]],["B",[1]],["C",[3]]] as const){
      for(const n of ["MUX_A0","MUX_A1","MUX_A2"])connected(`U_MUX_${ch}`,n.replace("MUX_",""),n)
      connected(`U_MUX_${ch}`,"EN","WING_EN");connected(`U_MUX_${ch}`,"D",`MUX_OUT_${ch}`)
      connected(`U_MUX_${ch}`,"VDD","HALL_5V");connected(`U_MUX_${ch}`,"GND","GND")
      ids.forEach((h,i)=>{connected(`U_H${h}`,"OUT",`H${h}_RAW`);connected(`U_MUX_${ch}`,`S${i+1}`,`H${h}_RAW`);connected(`C_HALL${h}`,"pin1","HALL_5V");connected(`C_HALL${h}`,"pin2","GND")})
      connected(`C_MUX_${ch}`,"pin1","HALL_5V");connected(`C_MUX_${ch}`,"pin2","GND")
    }
  }
  return {result:"PASS",component_count:comps.length,connector_return_contacts:6,
    components:comps.map(e=>({name:e.name,part:e.manufacturer_part_number??null,ftype:e.ftype}))}
}
const result={main:await inspect(mainPath,true),wing:await inspect(wingPath,false)}
await writeFile(output,JSON.stringify(result,null,2)+"\n");console.log("Representative scope and accepted G0B interface: PASS")
