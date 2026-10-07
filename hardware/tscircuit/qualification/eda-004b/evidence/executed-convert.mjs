import {readFileSync,writeFileSync} from 'node:fs'
import {CircuitJsonToKicadPcbConverter,CircuitJsonToKicadProConverter,CircuitJsonToKicadSchConverter} from 'circuit-json-to-kicad'
const [input,prefix]=process.argv.slice(2)
const json=JSON.parse(readFileSync(input,'utf8'))
for(const [extension,Class] of [['kicad_pcb',CircuitJsonToKicadPcbConverter],['kicad_pro',CircuitJsonToKicadProConverter],['kicad_sch',CircuitJsonToKicadSchConverter]]) {
 const converter=new Class(json,{projectName:'smoke'})
 converter.runUntilFinished()
 writeFileSync(`${prefix}.${extension}`,converter.getOutputString())
 console.log(extension,'written')
}
