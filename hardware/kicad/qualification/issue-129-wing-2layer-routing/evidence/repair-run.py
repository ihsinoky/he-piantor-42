"""Single routing invocation per cell; frozen repair inputs, original tool sources."""
from common import *
import sys,shutil
cell,tool,board=sys.argv[1:]
assert tool in ['KRT','FAB']
assert json.loads((E/'equivalence-gate.json').read_text())['pass_equivalence']
assert digest(E/'check-equivalence.py')==digest(E/'initial-run/check-equivalence.py')
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,11,4,23,56,tzinfo=datetime.timezone.utc)
w=E/'runs'/cell;w.mkdir(parents=True,exist_ok=False)
source=E/'inputs'/board
for f,h in json.loads((E/'input-hashes.json').read_text())[board].items():assert digest(source/f)==h
for ext in ['kicad_pcb','kicad_pro']:shutil.copy2(source/('main.'+ext),w/('in.'+ext))
shutil.copy2(source/'fp-lib-table',w/'fp-lib-table')
save(w/'launch.json',dict(cell=cell,tool=tool,board=board,utc=now(),single_run=True,input_sha256=digest(w/'in.kicad_pcb'),project_sha256=digest(w/'in.kicad_pro'),tool_options=['--escalation','off'] if tool=='KRT' else {'timeBudgetMs':1800000,'other':'API defaults'}))
if tool=='KRT':
 # Resolver readback exits before net selection; it does not route.
 assert run(cell+'-readback',[T/'venv/bin/python3',E/'repair-read-effective.py',w/'effective.json',board,'off'],timeout=120)==0
 rc=run(cell+'-route',[T/'venv/bin/python3','py_router/route.py',w/'in.kicad_pcb',w/'out.kicad_pcb','--escalation','off'],T/'KiCadRoutingTools',1800)
else:
 code='import pcbnew as p,sys; b=p.LoadBoard(sys.argv[1]); m=p.GetSettingsManager();m.LoadProject(sys.argv[2]);b.SetProject(m.Prj());assert p.ExportSpecctraDSN(b,sys.argv[3])'
 assert run(cell+'-export',['/usr/bin/python3','-c',code,w/'in.kicad_pcb',w/'in.kicad_pro',w/'input.dsn'],timeout=120)==0
 rc=run(cell+'-route',[T/'bun/bun-linux-x64/bun','run',E/'repair-driver.ts',T/'fab_router',w/'input.dsn',w],timeout=1920)
 if (w/'out.ses').exists():
  shutil.copy2(source/'main.kicad_pro',w/'out.kicad_pro')
  code='import pcbnew as p,sys; b=p.LoadBoard(sys.argv[1]);m=p.GetSettingsManager();m.LoadProject(sys.argv[2]);b.SetProject(m.Prj());assert p.ImportSpecctraSES(b,sys.argv[3]);assert p.SaveBoard(sys.argv[4],b)'
  irc=run(cell+'-import',['/usr/bin/python3','-c',code,w/'in.kicad_pcb',w/'out.kicad_pro',w/'out.ses',w/'out.kicad_pcb'],timeout=120)
  save(w/'import-result.json',{'exit_code':irc})
save(w/'execution.json',dict(exit_code=rc,input_unchanged=digest(w/'in.kicad_pcb')==digest(source/'main.kicad_pcb'),project_unchanged=digest(w/'in.kicad_pro')==digest(source/'main.kicad_pro'),outputs={f.name:digest(f) for f in w.iterdir() if f.is_file()}))
