import sys,json
from pathlib import Path
sys.path.insert(0,'/workspaces/he-piantor-42/hardware/kicad/qualification/eda-004f')
from capture import run,save,digest,utc
root=Path('/workspaces/he-piantor-42/hardware/kicad/qualification/eda-004f');base=Path('/tmp/eda004f');env=json.loads((root/'evidence/kicad-env.json').read_text());cli=str(base/'kicad/usr/bin/kicad-cli')
run('erc-help',[cli,'sch','erc','--help'],base,env=env)
run('netlist-help',[cli,'sch','export','netlist','--help'],base,env=env)
dest=base/'normal';dest.mkdir()
# Standard library configuration authored before the schematic; no ERC overrides.
(dest/'sym-lib-table').write_text('(sym_lib_table\n (version 7)\n'+''.join(f' (lib (name "{name}")(type "KiCad")(uri "{root}/library/{name}.kicad_sym")(options "")(descr "Pinned official library"))\n' for name in ['74xGxx','Device','power'])+')\n')
run('normal-generate',[str(base/'venv/bin/python'),'-B',str(root/'generate.py'),str(dest)],base,artifacts=[('fixture.kicad_sch',dest/'fixture.kicad_sch'),('sym-lib-table',dest/'sym-lib-table')])
