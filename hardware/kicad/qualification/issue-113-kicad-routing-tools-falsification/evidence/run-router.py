"""One default CLI invocation per stage, gated by frozen input and smoke acceptance."""
import runpy,shutil,sys
from pathlib import Path
E=Path(__file__).resolve().parent;globals().update(runpy.run_path(str(E/'prepare-inputs.py')))
stage=sys.argv[1];assert stage in ['smoke','main']
assert json.loads((E/'equivalence-gate.json').read_text())['pass_equivalence']
if stage=='main':assert json.loads((E/'smoke-gate.json').read_text())['pass']
w=E/'runs'/stage;w.mkdir(parents=True,exist_ok=False)
for ext in ['kicad_pcb','kicad_pro']:shutil.copyfile(E/'inputs'/stage/f'main.{ext}',w/f'in.{ext}')
source_hash=digest(w/'in.kicad_pcb');project_hash=digest(w/'in.kicad_pro')
save(w/'launch.json',dict(stage=stage,input_sha256=source_hash,project_sha256=project_hash,default_cli=True,options=[],utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),outer_timeout_seconds=1800))
rc=run(stage+'-route',[TMP/'venv/bin/python3','py_router/route.py',w/'in.kicad_pcb',w/'out.kicad_pcb'],TMP/'KiCadRoutingTools',1800)
save(w/'result.json',dict(exit_code=rc,input_unchanged=digest(w/'in.kicad_pcb')==source_hash,project_unchanged=digest(w/'in.kicad_pro')==project_hash,outputs={p.name:digest(p) for p in w.iterdir() if p.is_file()}))
