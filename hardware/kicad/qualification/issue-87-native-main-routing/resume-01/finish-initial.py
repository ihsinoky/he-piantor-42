"""Finish this single Main trial with KiCad+independent terminal inspection."""
from session import *
work=BASE/'main-initial-import'
record=json.loads((ROOT/'evidence/processes/main-initial-route/record.json').read_text())
assert record['end_utc'] and record['exit_code']==0 and not record['timed_out']
assert (BASE/'main-initial-route/output.ses').is_file()
save(ROOT/'evidence/assessment-freeze.json',dict(utc=utc(),main_attempt_registered=True,assessment_code_sha256=digest(ROOT/'assess-main.py'),graph_code_sha256=digest(PREV/'check-main.py'),note='Terminal measurement collection before verdict, reusing unchanged source geometry contract and graph; no router settings/input change or new route'))
run('main-initial-ses-import',['/usr/bin/python3',str(ROOT/'import-main.py')],BASE,env=ENV,artifacts=[('main.kicad_pcb',work/'main.kicad_pcb'),('main.kicad_pro',work/'main.kicad_pro')])
run('main-initial-read-return',['/usr/bin/python3',str(OLD/'read-pcb.py'),str(work/'main.kicad_pcb'),str(work/'snapshot.json')],work,env=ENV,artifacts=[('snapshot.json',work/'snapshot.json')])
run('main-initial-return-drc',[str(CLI),'pcb','drc','--format','json','--severity-all','-o',str(work/'drc.json'),str(work/'main.kicad_pcb')],work,env=ENV,artifacts=[('drc.json',work/'drc.json')])
run('main-initial-assessment',[str(GEOM),str(ROOT/'assess-main.py'),'/tmp/issue87/main/main.kicad_pcb',str(work/'main.kicad_pcb'),str(PREV/'evidence/processes/baseline-read/snapshot.json'),str(work/'snapshot.json'),str(work/'drc.json'),str(ROOT/'evidence/main-initial-assessment.json')],work,180)
r=json.loads((ROOT/'evidence/main-initial-assessment.json').read_text());ledger=json.loads((ROOT/'evidence/attempt-ledger.json').read_text());ledger['initial_all_conditions_pass']=r['all_conditions_pass'];ledger['initial_assessment_sha256']=digest(ROOT/'evidence/main-initial-assessment.json');save(ROOT/'evidence/attempt-ledger.json',ledger)
if not r['all_conditions_pass']:
    save(ROOT/'evidence/stop-decision.json',dict(utc=utc(),classification='ROUTING_BLOCKED / FIXED_MAIN_INITIAL_FAIL / MAIN_UNQUALIFIED',first_terminal_gate='D: first fixed Main route returned-board acceptance',reason='Initial fixed Main fails KiCad and/or independent terminal acceptance; see exact actual-copper/DRC/transfer metrics, not process exit/router success',assessment_sha256=digest(ROOT/'evidence/main-initial-assessment.json'),small_attempts=1,main_initial_attempts=1,confirmation_attempts=0,experiment_restart_forbidden=True,after_stop='Evidence organization/report/submission/static saved-evidence verification only; no confirmation/retry/settings search/repair/product work',not_method_wide_infeasibility=True))
    print('STOP: fixed Main initial failed; no confirmation or retry')
else:print('Initial all-condition PASS; fresh regeneration confirmation prerequisite now opens')
