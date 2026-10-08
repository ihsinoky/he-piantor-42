import assert from 'node:assert/strict'
import {readFileSync} from 'node:fs'
import {CircuitJsonToKicadPcbConverter as Pcb,CircuitJsonToKicadSchConverter as Sch} from 'circuit-json-to-kicad'
const data=JSON.parse(readFileSync(process.argv[2],'utf8'))
const results=[]
function output(C,d) {const c=new C(d,{projectName:'smoke'});c.runUntilFinished();return c.getOutputString()}
function fault(name,C,change,pattern) {const d=structuredClone(data);change(d);assert.throws(()=>output(C,d),pattern);results.push({name,status:'DETECTED'})}
const pcb=output(Pcb,data),sch=output(Sch,data)
assert.match(pcb,/\(net \d+ "GND"\)/)
assert.match(sch,/\(pin output line/);assert.match(sch,/\(pin input line/)
results.push({name:'positive explicit output and input',status:'PASS'})
fault('internal duplicate land assigned SIG',Pcb,d=>{
 const sig=d.find(x=>x.type==='source_port'&&x.name==='OUT')
 d.find(x=>x.type==='source_port'&&x.name==='pin2_internal_1').subcircuit_connectivity_map_key=sig.subcircuit_connectivity_map_key
},/multiple KiCad nets/)
fault('internal cross-component relationship',Pcb,d=>{
 d.find(x=>x.type==='source_component_internal_connection').source_port_ids.push('source_port_3')
},/Invalid internal connection/)
fault('unknown internal port',Pcb,d=>{
 d.find(x=>x.type==='source_component_internal_connection').source_port_ids.push('missing_port')
},/Invalid internal connection/)
fault('missing explicit input type',Sch,d=>{delete d.find(x=>x.type==='source_port'&&x.name==='IN').is_input},/Missing or conflicting electrical type/)
fault('conflicting input/output type',Sch,d=>{d.find(x=>x.type==='source_port'&&x.name==='IN').is_output=true},/Missing or conflicting electrical type/)
fault('conflicting output modes',Sch,d=>{const p=d.find(x=>x.type==='source_port'&&x.name==='OUT');p.is_using_tri_state=true;p.is_using_open_collector=true},/Conflicting output mode/)
for(const [flag,kind] of [['is_bidirectional','bidirectional'],['is_passive','passive'],['provides_power','power_out'],['requires_power','power_in'],['do_not_connect','no_connect']]) {
 const d=structuredClone(data),p=d.find(x=>x.type==='source_port'&&x.name==='IN');delete p.is_input;p[flag]=true
 assert.match(output(Sch,d),new RegExp('\\(pin '+kind+' line'));results.push({name:flag,status:'PASS'})
}
for(const [flag,kind] of [['is_using_tri_state','tri_state'],['is_using_open_collector','open_collector'],['is_using_open_emitter','open_emitter']]) {
 const d=structuredClone(data);d.find(x=>x.type==='source_port'&&x.name==='OUT')[flag]=true
 assert.match(output(Sch,d),new RegExp('\\(pin '+kind+' line'));results.push({name:flag,status:'PASS'})
}
console.log(JSON.stringify({status:'PASS',tests:results,scope:'converter unit tests on copies; no routed artifacts or file repair'},null,2))
