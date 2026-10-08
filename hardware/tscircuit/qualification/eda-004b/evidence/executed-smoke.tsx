import React from "react"
import { Circuit } from "tscircuit"
import { writeFileSync } from "node:fs"

// One synthetic transport fixture. Electrical semantics are defined by this
// test source, not inferred from pin names or claimed for a real part.
const pad = (pin:string,x:number,y:number) => <smtpad shape="rect" layer="top"
  pcbX={x} pcbY={y} width={1} height={1} portHints={[pin]}/>
const c = new Circuit()
c.add(<board width={20} height={16} layers={2} thickness="1.2mm"
  routingDisabled minTraceWidth="0.2mm" defaultTraceWidth="0.2mm"
  minTraceToPadEdgeClearance="0.2mm" minViaHoleDiameter="0.3mm" minViaPadDiameter="0.6mm">
  <chip name="U_TX" pcbX={-4} pcbY={0} schX={-4} pinLabels={{pin1:"OUT",pin2:"GND"}}
    pinAttributes={{OUT:{isOutput:true},GND:{isPassive:true}}}
    footprint={<footprint>{pad("pin1",0,2)}
      <platedhole shape="oval" pcbX={-1} pcbY={0} holeWidth={0.6} holeHeight={1.7} outerWidth={1} outerHeight={2.1} portHints={["pin2"]}/>
      <platedhole shape="oval" pcbX={1} pcbY={0} holeWidth={0.6} holeHeight={1.2} outerWidth={1} outerHeight={1.6} portHints={["pin2"]}/>
      <hole pcbX={0} pcbY={-3} diameter={0.65}/>
    </footprint>}/>
  <chip name="U_RX" pcbX={4} pcbY={0} schX={4} pinLabels={{pin1:"IN",pin2:"GND"}}
    pinAttributes={{IN:{isInput:true},GND:{isPassive:true}}}
    footprint={<footprint>{pad("pin1",0,2)}{pad("pin2",0,0)}</footprint>}/>
  <net name="SIG"/><net name="GND" isGroundNet/>
  <trace from=".U_TX > .OUT" to="net.SIG"/>
  <trace from=".U_RX > .IN" to="net.SIG"/>
  <trace from=".U_TX > .GND" to="net.GND"/>
  <trace from=".U_RX > .GND" to="net.GND"/>
  <trace name="LOCAL_BOND" from=".U_TX > .GND" to="net.GND" thickness="0.2mm"
    pcbPath={[{x:-1,y:0},{x:1,y:0},{x:-1,y:0}]}/>
</board>)
await c.renderUntilSettled()
const json=c.getCircuitJson()
if(json.some((x:any)=>["pcb_trace","pcb_via","pcb_copper_pour"].includes(x.type)))
  throw new Error("routingDisabled retained copper; STOP")
writeFileSync(process.argv[2],JSON.stringify(json,null,2)+"\n")
console.log(JSON.stringify({routingDisabled:true,globalTracks:0,vias:0,sourceTraces:json.filter((x:any)=>x.type==="source_trace").length}))
