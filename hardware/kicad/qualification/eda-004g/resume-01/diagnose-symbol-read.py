"""Read-only diagnosis of public serializer/library compatibility, no routing."""
from pathlib import Path
import json
import kicad_sch_api as ksa
from kicad_sch_api.library.cache import set_symbol_cache
from capture import ROOT,run,save
cache=ksa.SymbolLibraryCache(enable_persistence=False);cache.discover_libraries([str(ROOT/'library')]);set_symbol_cache(cache)
env=json.loads((ROOT/'evidence/resume-kicad-env.json').read_text())
ids=list(dict.fromkeys(c['lib_id'] for c in json.loads((ROOT/'main-contract-v1.json').read_text())['components']))
results=[]
for i,lib in enumerate(ids):
    sch=ksa.create_schematic('public-symbol-read-diagnostic');sch.components.add(lib,'U1','probe',position=(76.2,76.2))
    path=Path(f'/tmp/eda004g-resume01/diagnostic-{i}.kicad_sch');sch.save(str(path))
    try:
        record=run(f'symbol-read-diagnostic-{i}',['/tmp/eda004g/kicad/usr/bin/kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(path.with_suffix('.xml')),str(path)],ROOT,env=env,artifacts=[('input.kicad_sch',path),('output.xml',path.with_suffix('.xml'))]);passed=True
    except RuntimeError:passed=False
    results.append(dict(lib_id=lib,public_cli_load=passed))
save(ROOT/'evidence/symbol-read-diagnosis.json',results);print(results)
