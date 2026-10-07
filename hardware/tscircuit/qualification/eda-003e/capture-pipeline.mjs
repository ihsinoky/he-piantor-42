// Observation only: prototype wrapper on the public stock Pipeline9 class.
// Transpile unchanged accepted TSX copies in /tmp because Bun is absent.
import fs from 'node:fs'
import path from 'node:path'
import {createRequire} from 'node:module'
import {fileURLToPath} from 'node:url'
const here=path.dirname(fileURLToPath(import.meta.url))
const stock=path.resolve(here,'../eda-003c/latest-stock')
const require=createRequire(stock+'/package.json')
const ts=require('typescript')
const out=process.argv[2]
if(!out || fs.existsSync(out)) throw Error('Supply an absent absolute /tmp output directory')
if(!out.startsWith('/tmp/')) throw Error('Experiment must be under /tmp')
fs.mkdirSync(out,{recursive:true})
fs.symlinkSync(stock+'/node_modules',out+'/node_modules')
fs.writeFileSync(out+'/package.json','{"type":"module"}')
for(const name of ['src/qualification/revm1-routing-proof.tsx','src/qualification/JstGh14.tsx','src/qualification/native-support-footprints.tsx','src/components/HallKey.tsx']) {
 const result=ts.transpileModule(fs.readFileSync(stock+'/'+name,'utf8'),{compilerOptions:{jsx:ts.JsxEmit.React,module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2022}}).outputText.replace(/from "(\.[^"]+)"/g,'from "$1.js"')
 const dest=out+'/'+name.replace(/\.tsx$/,'.js');fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,result)
}
fs.writeFileSync(out+'/run.mjs',`
import fs from 'node:fs';
import React from 'react';
import { Circuit } from '@tscircuit/core';
import {AutoroutingPipelineSolver9_PreloadedTraceGraph as Pipeline} from '@tscircuit/capacity-autorouter';
import {RepresentativeMain} from './src/qualification/revm1-routing-proof.js';
const save=(name,value)=>fs.writeFileSync(new URL(name+'.json',import.meta.url),JSON.stringify(value,null,2));
const original=Pipeline.prototype._step;
Pipeline.prototype._step=function(){
 const phase=this.getCurrentPhase(), active=this.activeSubSolver;
 if(!this.__capturedInput){save('input',this.originalSrj);this.__capturedInput=true;}
 original.call(this);
 if(this.getCurrentPhase()!==phase){
  let output;
  try {output=active?.getOutput?.()} catch(e) {output={capture_error:String(e)}}
  save(phase,{phase,output,routes:active?.routes,hdRoutes:active?.hdRoutes,simplifiedHdRoutes:active?.simplifiedHdRoutes,mergedHdRoutes:active?.mergedHdRoutes});
  console.log(phase);
 }
 if(this.solved) save('solver-output',this.getOutputSimplifiedPcbTraces());
};
const timer=setTimeout(()=>{console.error('300s observational deadline');process.exit(2)},300000);
const c=new Circuit();c.add(React.createElement(RepresentativeMain,{strategy:3}));
try {await c.renderUntilSettled();save('circuit',c.getCircuitJson());} finally {clearTimeout(timer)}
`)
console.log(out+'/run.mjs')
