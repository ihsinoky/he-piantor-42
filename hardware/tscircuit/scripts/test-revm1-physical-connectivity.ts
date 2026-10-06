import assert from "node:assert/strict"
import { verifyPhysical, type E } from "./revm1-physical-connectivity"

// Independent fault fixtures: endpoint IDs and logical membership must never
// substitute for copper. These are test data, not edits to generated boards.
const fixture = (): E[] => [
  {type:"source_component",source_component_id:"u",name:"U"},
  {type:"source_net",source_net_id:"n",name:"GND"},
  ...[0,1].flatMap(i=>[
    {type:"source_port",source_port_id:`s${i}`,source_component_id:"u",name:`P${i}`},
    {type:"pcb_port",pcb_port_id:`p${i}`,source_port_id:`s${i}`},
    {type:"pcb_smtpad",pcb_smtpad_id:`pad${i}`,pcb_port_id:`p${i}`,shape:"rect",x:i*10,y:0,width:1,height:1,layer:"top"},
    {type:"source_trace",connected_source_port_ids:[`s${i}`],connected_source_net_ids:["n"]},
  ]),
  {type:"pcb_trace",pcb_trace_id:"t",start_pcb_port_id:"p0",end_pcb_port_id:"p1",
    route:[{route_type:"wire",x:0,y:0,width:.2,layer:"top"},{route_type:"wire",x:10,y:0,width:.2,layer:"top"}]},
]
let checks=0
const expect=(f:E[],complete:boolean,unrouted?:number)=>{
  const r=verifyPhysical(f);assert.equal(r.complete,complete)
  if(unrouted!==undefined)assert.equal(r.electrically_required_unrouted_count,unrouted)
  checks++;return r
}
expect(fixture(),true,0)
const noCopper=fixture().filter(x=>x.type!=="pcb_trace");expect(noCopper,false,1)
const gap=fixture();gap.find(x=>x.type==="pcb_trace")!.route[1].x=9;expect(gap,false,1)
const bottom=fixture();bottom.find(x=>x.type==="pcb_trace")!.route.forEach((x:E)=>x.layer="bottom");expect(bottom,false,1)
const missing=fixture().filter(x=>x.pcb_port_id!=="p1"||x.type==="pcb_port");expect(missing,false,1)
const bridged=fixture();bridged.find(x=>x.type==="pcb_trace")!.route=[
  {route_type:"wire",x:0,y:0,width:.2,layer:"top"},
  {route_type:"via",x:5,y:0,from_layer:"bottom",to_layer:"top"},
  {route_type:"wire",x:5,y:0,width:.2,layer:"bottom"},
  {route_type:"wire",x:10,y:0,width:.2,layer:"bottom"},
]
bridged.find(x=>x.type==="pcb_smtpad"&&x.pcb_port_id==="p1")!.layer="bottom"
bridged.push({type:"pcb_via",pcb_via_id:"v",x:5,y:0,hole_diameter:.3,outer_diameter:.6,layers:["top","bottom"]})
expect(bridged,true,0) // deliberately reversed route order at the via
expect(bridged.filter(x=>x.type!=="pcb_via"),false)
const transition=fixture();transition.find(x=>x.type==="pcb_trace")!.route[1].layer="bottom"
assert.ok(expect(transition,false).invalid_layer_transitions.length)
const short=fixture();short.push({type:"source_net",source_net_id:"other",name:"OTHER"})
short.find(x=>x.type==="source_trace"&&x.connected_source_port_ids[0]==="s1")!.connected_source_net_ids=["other"]
assert.equal(expect(short,false).wrong_net_copper_components.length,1)
const internal=noCopper.concat({type:"source_component_internal_connection",source_port_ids:["s0","s1"]})
expect(internal,false,1)
const nc=fixture();nc.push({type:"source_port",source_port_id:"nc",source_component_id:"u",name:"NC",do_not_connect:true})
assert.equal(expect(nc,true,0).intentional_nc_count,1)
const unsupported=fixture();unsupported.find(x=>x.type==="pcb_smtpad")!.shape="polygon"
assert.ok(expect(unsupported,false).unsupported_geometry.length)
console.log(JSON.stringify({result:"PASS",fault_fixture_checks:checks}))
