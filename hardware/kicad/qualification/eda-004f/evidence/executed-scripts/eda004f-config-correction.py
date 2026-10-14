import sys,json
from pathlib import Path
sys.path.insert(0,'hardware/kicad/qualification/eda-004f')
from capture import run,save,digest,utc
root=Path('hardware/kicad/qualification/eda-004f').resolve();base=Path('/tmp/eda004f');dest=base/'normal';env=json.loads((root/'evidence/kicad-env.json').read_text());cli=str(base/'kicad/usr/bin/kicad-cli')
config=base/'config/kicad/9.0';config.mkdir(parents=True,exist_ok=True)
(config/'sym-lib-table').write_bytes((dest/'sym-lib-table').read_bytes())
save(root/'evidence/configuration-correction.json',{'recorded_utc':utc(),'initial_erc':'processes/normal-erc/erc.json','initial_acceptance':'FAIL: six lib_symbol_issues warnings','reason':'Standalone CLI schematic does not load neighboring project table without a project; register same pinned libraries in isolated KiCad global config','diff':'Identical sym-lib-table copied to XDG_CONFIG_HOME/kicad/9.0/sym-lib-table; schematic/contract/author unchanged','before_schematic_sha256':digest(dest/'fixture.kicad_sch'),'table_sha256':digest(config/'sym-lib-table'),'suppression':False})
try:run('normal-erc-configured',[cli,'sch','erc','--format','json','--severity-all','--exit-code-violations','-o',str(dest/'erc.json'),str(dest/'fixture.kicad_sch')],dest,env=env,artifacts=[('erc.json',dest/'erc.json'),('sym-lib-table',config/'sym-lib-table')])
except RuntimeError:print('nonzero: inspect')
run('normal-reconcile',[str(base/'venv/bin/python'),'-B',str(root/'reconcile.py'),str(dest),'--output',str(dest/'reconciliation.json')],dest,artifacts=[('reconciliation.json',dest/'reconciliation.json')])
print((dest/'reconciliation.json').read_text())
