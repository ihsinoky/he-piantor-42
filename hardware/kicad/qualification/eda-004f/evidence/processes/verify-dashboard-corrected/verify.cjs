const fs=require('fs'),vm=require('vm'),assert=require('assert');
const data=fs.readFileSync('task/data/project-status.js','utf8'),ui=fs.readFileSync('task/dashboard.js','utf8');
function render(substitute) {
 const elements=new Map();
 const document={getElementById(id){if(!elements.has(id))elements.set(id,{textContent:'',innerHTML:'',href:'',value:'',className:'',addEventListener(){},insertAdjacentHTML(_,s){this.innerHTML+=s;}});return elements.get(id);}};
 const context={window:{},document};vm.runInNewContext(data,context);
 if(substitute)substitute(context.window.PROJECT_STATUS);
 vm.runInNewContext(ui,context);return {elements,status:context.window.PROJECT_STATUS};
}
const a=render();assert(a.elements.get('evaluation-id').textContent.includes('EDA-004F'));assert(a.elements.get('report-link').href==='../docs/headless-schematic-qualification.md');assert(a.elements.get('issue-link').textContent==='Issue #83');assert(a.elements.get('qualification-map').innerHTML.includes('EDA-004F'));
const b=render(p=>{p.latestEvaluation={...p.latestEvaluation,id:'TEMP-ONLY',title:'Temporary evaluation',workStatus:'temporary work',technicalStatus:'temporary result',currentSummary:'temporary current',issue:{id:'999',url:'https://example.invalid/issue'},acceptedRecord:{id:'999',url:'https://example.invalid/pr',status:'temporary'}};p.source.reportUrl='../docs/temporary-only.md';});
assert(b.elements.get('evaluation-id').textContent==='評価 TEMP-ONLY');assert(b.elements.get('evaluation-title').textContent==='Temporary evaluation');assert(b.elements.get('current-change').textContent==='temporary current');assert(b.elements.get('work-status').textContent==='temporary work');assert(b.elements.get('technical-status').textContent==='temporary result');assert(b.elements.get('report-link').href==='../docs/temporary-only.md');assert(b.elements.get('report-link').textContent.includes('TEMP-ONLY'));assert(b.elements.get('qualification-map').innerHTML.includes('TEMP-ONLY'));assert(!b.elements.get('qualification-map').innerHTML.includes('EDA-004F'));assert(b.elements.get('pr-link').textContent.includes('#999'));
for(const key of ['plan','milestones','gates','risks'])assert(a.status[key]);
console.log(JSON.stringify({javascriptSyntax:true,currentEvaluation:'EDA-004F',temporaryRecordSubstitution:'PASS',temporaryDataPersisted:false,renderMethod:'Node vm DOM stub; no real browser/visual check claimed'},null,2));
