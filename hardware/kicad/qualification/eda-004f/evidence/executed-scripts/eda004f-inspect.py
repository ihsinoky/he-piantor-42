import sys,json
from pathlib import Path
sys.path.insert(0,'/workspaces/he-piantor-42/hardware/kicad/qualification/eda-004f')
from capture import run,save,digest,utc
root=Path('/workspaces/he-piantor-42/hardware/kicad/qualification/eda-004f');base=Path('/tmp/eda004f');env=json.loads((root/'evidence/kicad-env.json').read_text());cli=str(base/'kicad/usr/bin/kicad-cli');dest=base/'normal'
for name,args,out in [('netlist',['sch','export','netlist','--format','kicadxml'],'fixture.xml'),('erc',['sch','erc','--format','json','--severity-all','--exit-code-violations'],'erc.json')]:
 try:run('normal-'+name,[cli,*args,'-o',str(dest/out),str(dest/'fixture.kicad_sch')],dest,env=env,artifacts=[(out,dest/out)])
 except RuntimeError: print(name+' nonzero; inspect raw before any further experiment')
print((dest/'erc.json').read_text())
