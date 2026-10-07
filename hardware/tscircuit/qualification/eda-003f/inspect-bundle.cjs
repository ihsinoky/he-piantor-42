// Enumerate exact installed runtime target expressions using the stock TS parser.
const fs=require('node:fs'),{createRequire}=require('node:module');
const env=process.argv[2],req=createRequire(env+'/package.json'),ts=req('typescript');
const code=fs.readFileSync(env+'/node_modules/@tscircuit/capacity-autorouter/dist/index.js','utf8');
const ast=ts.createSourceFile('index.js',code,ts.ScriptTarget.Latest,true),functions=[];
function walk(node){
 if(ts.isArrowFunction(node)||ts.isFunctionExpression(node)||ts.isFunctionDeclaration(node)){
  const text=node.getText(ast);
  if(text.length<10000&&((text.includes('rootConnectionName')&&text.includes('Math.hypot')&&/\.radius\+\w+\.radius\+.*\+ow-/.test(text)&&text.includes('pointTo')===false)||(text.includes('s.radius+o.traceRadius+')&&text.includes('movable'))))functions.push({start:node.getStart(ast),end:node.end,text});
 }
 ts.forEachChild(node,walk);
}
walk(ast);
if(ast.parseDiagnostics.length)throw Error('Bundle fails JS parsing');
console.log(JSON.stringify({parse_diagnostics:0,functions},null,2));
