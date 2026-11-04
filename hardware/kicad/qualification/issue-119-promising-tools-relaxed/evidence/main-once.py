from common import *
import concurrent.futures
assert json.loads((E/'smoke-gate.json').read_text())['pass']
assert (E/'runtime-revalidation.json').exists()
# Freeze all execution and inspection scripts before any Main output exists.
save(E/'main-freeze.json',dict(utc=utc(),cells={'A':['main4','fab'],'B':['main4','krt'],'C':['main4','free'],'D':['main2','fab']},run_limit_per_cell=1,rerun_forbidden=True,scripts={p.name:sha(p) for p in E.glob('*.py')},driver_sha256=sha(E/'driver.ts'),equivalence_gate_sha256=sha(E/'equivalence-gate.json'),smoke_gate_sha256=sha(E/'smoke-gate.json'),timeouts_seconds=dict(fab=1920,krt=1800,free=1260),freerouting_configuration_lineage='Issue 95 Run 2; fanout and optimizer enabled; all algorithm flags identical'))
def cell(pair):
 label,router=pair
 rc=run(label+'-'+router+'-launcher',['/usr/bin/python3',E/'run-cell.py',label,router],timeout=1950)
 if rc==0:
  assert run(label+'-'+router+'-inspection',['/usr/bin/python3',E/'independent-check.py',label,router],timeout=240)==0
 return dict(label=label,router=router,exit_code=rc)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 results=list(pool.map(cell,[('main4','fab'),('main4','krt'),('main4','free'),('main2','fab')]))
save(E/'main-executions.json',dict(utc=utc(),results=results))
