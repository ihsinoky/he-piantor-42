/** Read-only physical copper graph. No routing, repair, or generated-data edit.
 * Supports the fixture's rectangular/circular SMT pads, circular/oval PTHs,
 * wire segments and circular through vias on the two physical layers.
 * Source membership defines which connections are required; ONLY geometry
 * joins the physical graph. Even duplicate/internal source ports must have
 * connected copper. Unsupported copper fails closed rather than being omitted.
 */
export type E = Record<string, any>
type P = { x:number; y:number }
type Shape={ id:string; layer:string; polygon?:P[]; a?:P; b?:P; radius?:number }
class Union {
  p=new Map<string,string>()
  find(a:string):string {if(!this.p.has(a))this.p.set(a,a);const b=this.p.get(a)!;if(b!==a)this.p.set(a,this.find(b));return this.p.get(a)!}
  join(a:string,b:string){this.p.set(this.find(a),this.find(b))}
  group(ids:string[]){for(const a of ids)this.join(ids[0],a)}
}
const eps=1e-6
const sub=(a:P,b:P)=>({x:a.x-b.x,y:a.y-b.y})
const cross=(a:P,b:P)=>a.x*b.y-a.y*b.x
const pointSegment=(p:P,a:P,b:P)=>{
  const v=sub(b,a), t=Math.max(0,Math.min(1,((p.x-a.x)*v.x+(p.y-a.y)*v.y)/(v.x*v.x+v.y*v.y||1)))
  return Math.hypot(p.x-a.x-t*v.x,p.y-a.y-t*v.y)
}
const segments=(a:P,b:P,c:P,d:P)=>{
  const ab=sub(b,a),cd=sub(d,c),den=cross(ab,cd)
  if(Math.abs(den)>eps){const ac=sub(c,a),t=cross(ac,cd)/den,u=cross(ac,ab)/den;if(t>=0&&t<=1&&u>=0&&u<=1)return 0}
  return Math.min(pointSegment(a,c,d),pointSegment(b,c,d),pointSegment(c,a,b),pointSegment(d,a,b))
}
const inside=(p:P,poly:P[])=>{
  let yes=false
  for(let i=0,j=poly.length-1;i<poly.length;j=i++){
    const a=poly[i],b=poly[j];if(pointSegment(p,a,b)<eps)return true
    if((a.y>p.y)!==(b.y>p.y)&&p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x)yes=!yes
  }return yes
}
const edges=(p:P[])=>p.map((a,i)=>[a,p[(i+1)%p.length]] as [P,P])
const distance=(a:Shape,b:Shape):number=>{
  if(a.polygon&&b.polygon){
    if(inside(a.polygon[0],b.polygon)||inside(b.polygon[0],a.polygon))return 0
    return Math.min(...edges(a.polygon).flatMap(([p,q])=>edges(b.polygon!).map(([r,s])=>segments(p,q,r,s))))
  }
  if(a.polygon){if(inside(b.a!,a.polygon)||inside(b.b!,a.polygon))return -(b.radius??0)
    return Math.min(...edges(a.polygon).map(([p,q])=>segments(p,q,b.a!,b.b!)))-(b.radius??0)}
  if(b.polygon)return distance(b,a)
  return segments(a.a!,a.b!,b.a!,b.b!)-(a.radius??0)-(b.radius??0)
}

export function verifyPhysical(json:E[]){
  const of=(t:string)=>json.filter(x=>x.type===t), logical=new Union(), physical=new Union()
  const ports=of("source_port"), pcbPorts=of("pcb_port"), nets=of("source_net")
  const requiredSource=new Set<string>()
  for(const t of of("source_trace")){
    const ids=[...(t.connected_source_port_ids??[]),...(t.connected_source_net_ids??[])];logical.group(ids)
    for(const id of t.connected_source_port_ids??[])requiredSource.add(id)
  }
  for(const c of of("source_component_internal_connection"))logical.group(c.source_port_ids)
  // Include all source members of required internal groups, but NEVER use them
  // to join the physical graph (e.g. Hall SMD ground and ground PTH).
  const needed=new Set([...requiredSource].map(x=>logical.find(x)))
  for(const p of ports)if(needed.has(logical.find(p.source_port_id))&&!p.do_not_connect)requiredSource.add(p.source_port_id)
  const unassigned=ports.filter(p=>!p.do_not_connect&&!requiredSource.has(p.source_port_id))
  const shapes:Shape[]=[], unsupported:string[]=[], layerErrors:string[]=[]
  const rect=(id:string,layer:string,x:number,y:number,w:number,h:number,angle=0)=>{
    const r=angle*Math.PI/180
    shapes.push({id,layer,polygon:[[-w/2,-h/2],[w/2,-h/2],[w/2,h/2],[-w/2,h/2]].map(([a,b])=>({x:x+a*Math.cos(r)-b*Math.sin(r),y:y+a*Math.sin(r)+b*Math.cos(r)}))})
  }
  const capsule=(id:string,layer:string,x:number,y:number,w:number,h:number)=>{
    const radius=Math.min(w,h)/2
    shapes.push({id,layer,radius,a:{x:x-Math.max(0,w-h)/2,y:y-Math.max(0,h-w)/2},b:{x:x+Math.max(0,w-h)/2,y:y+Math.max(0,h-w)/2}})
  }
  const pads=[...of("pcb_smtpad"),...of("pcb_plated_hole")]
  for(const p of pads){
    const id=p.pcb_port_id??p.pcb_smtpad_id??p.pcb_plated_hole_id
    const layers=p.layer?[p.layer]:p.layers??["top","bottom"]
    for(const l of layers){
      if(p.shape==="rect")rect(id,l,p.x,p.y,p.width,p.height,p.ccw_rotation??0)
      else if(p.shape==="circle")capsule(id,l,p.x,p.y,p.outer_diameter??p.radius*2,p.outer_diameter??p.radius*2)
      else if(p.shape==="oval")capsule(id,l,p.x,p.y,p.outer_width,p.outer_height)
      else unsupported.push(`${p.type}:${p.shape}`)
    }
  }
  const vias=of("pcb_via")
  for(const v of vias){
    if(v.hole_diameter<=0||v.outer_diameter<=v.hole_diameter||v.layers?.length!==2||!v.layers.includes("top")||!v.layers.includes("bottom"))layerErrors.push(`Invalid via ${v.pcb_via_id}`)
    for(const l of v.layers??[])capsule(v.pcb_via_id,l,v.x,v.y,v.outer_diameter,v.outer_diameter)
  }
  for(const t of of("pcb_trace")){
    const route=t.route??[]
    for(let i=0;i<route.length-1;i++){
      const a=route[i],b=route[i+1],id=`${t.pcb_trace_id}:${i}`
      // A plated via is undirected copper. Stock can reverse route ordering
      // without swapping from_layer/to_layer. Check layer span, not traversal.
      const layer=a.route_type==="via"?b.layer:a.layer
      const endLayer=b.route_type==="via"?a.layer:b.layer
      if(a.route_type==="via"&&![a.from_layer,a.to_layer].includes(layer))layerErrors.push(`Wire outside via span ${id}`)
      if(b.route_type==="via"&&![b.from_layer,b.to_layer].includes(layer))layerErrors.push(`Wire outside via span ${id}`)
      if(layer!==endLayer){layerErrors.push(`Unbridged transition ${id}`);continue}
      if(!["top","bottom"].includes(layer)){layerErrors.push(`Invalid layer ${id}`);continue}
      const width=a.width??b.width
      if(!Number.isFinite(width)||width<=0){unsupported.push(`Missing wire width ${id}`);continue}
      shapes.push({id,layer,a,b,radius:width/2})
    }
    for(const p of route.filter((x:E)=>x.route_type==="via")){
      if(!vias.some(v=>Math.hypot(v.x-p.x,v.y-p.y)<eps&&v.layers.includes(p.from_layer)&&v.layers.includes(p.to_layer)))layerErrors.push(`Missing materialized via in ${t.pcb_trace_id}`)
    }
  }
  if(of("pcb_copper_pour").length)unsupported.push("Copper pours are outside this fixture verifier's geometry coverage")
  for(const s of shapes)physical.find(s.id)
  for(let i=0;i<shapes.length;i++)for(let j=0;j<i;j++){
    const a=shapes[i],b=shapes[j]
    if(a.layer===b.layer&&distance(a,b)<=eps)physical.join(a.id,b.id)
  }
  const groups=new Map<string,{names:string[];source:string[];pcb:string[];missing:string[]}>()
  for(const id of requiredSource){
    const root=logical.find(id), g=groups.get(root)??{names:[],source:[],pcb:[],missing:[]}
    g.source.push(id);const pp=pcbPorts.filter(x=>x.source_port_id===id)
    if(!pp.length)g.missing.push(id)
    for(const p of pp){g.pcb.push(p.pcb_port_id);if(!shapes.some(s=>s.id===p.pcb_port_id))g.missing.push(id)}
    groups.set(root,g)
  }
  for(const n of nets){const g=groups.get(logical.find(n.source_net_id));if(g)g.names.push(n.name)}
  const comp=Object.fromEntries(of("source_component").map(x=>[x.source_component_id,x.name]))
  const name=(id:string)=>{const p=ports.find(p=>p.source_port_id===id);return p?`${comp[p.source_component_id]}.${p.name}`:id}
  let unrouted=0,endpoints=0
  const netResults=[...groups.values()].map(g=>{
    const roots=new Set(g.pcb.filter(id=>shapes.some(s=>s.id===id)).map(id=>physical.find(id)))
    const missing=new Set(g.missing)
    const deficit=Math.max(0,roots.size-1)+missing.size
    unrouted+=deficit;endpoints+=g.pcb.length+missing.size
    const islands=[...roots].map(root=>g.pcb.filter(id=>physical.find(id)===root).map(id=>{
      const p=pcbPorts.find(p=>p.pcb_port_id===id);return `${name(p?.source_port_id)}:${id}`
    }))
    return {nets:g.names,required_endpoints:g.pcb.length+missing.size,copper_islands:roots.size,
      disconnected_islands:deficit?islands:[],missing_physical_ports:[...missing].map(name),unrouted_connections:deficit}
  })
  const physicalNetSets=new Map<string,Set<string>>()
  for(const [root,g] of groups)for(const p of g.pcb){const r=physical.find(p),s=physicalNetSets.get(r)??new Set();s.add(root);physicalNetSets.set(r,s)}
  const shorts=[...physicalNetSets.values()].filter(s=>s.size>1).map(s=>[...s].map(r=>groups.get(r)?.names))
  return {source_net_count:nets.length,required_physical_endpoint_count:endpoints+unassigned.length,routed_trace_count:of("pcb_trace").length,
    via_count:vias.length,electrically_required_unrouted_count:unrouted+unassigned.length,intentional_nc_count:ports.filter(p=>p.do_not_connect).length,
    unassigned_non_nc_ports:unassigned.map(p=>name(p.source_port_id)),
    wrong_net_copper_components:shorts,unsupported_geometry:unsupported,invalid_layer_transitions:layerErrors,net_results:netResults,
    complete:unrouted===0&&unassigned.length===0&&shorts.length===0&&unsupported.length===0&&layerErrors.length===0}
}
