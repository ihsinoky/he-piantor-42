from helpers import *
checks={}
for router in ['fab','krt']:
 w=A/'inspection/smoke-02'/router
 d=json.loads((w/'independent.json').read_text());assert d['pass_acceptance'] and all(v==0 for v in d['metrics'].values())
 assert d['plane_role_pass'] and d['physical']['In1_signal_tracks']==0
 assert json.loads((E/'processes'/('amend01-smoke-02-'+router+'-route')/'record.json').read_text())['exit_code']==0
 checks[router]=dict(metrics=d['metrics'],In1_tracks=0,headless=True,output_generated=True,KiCad_readback_and_refill=True,independent_result_sha256=sha(w/'independent.json'))
for path,row in json.loads((A/'main-reuse-and-runtime-revalidation.json').read_text())['files'].items():assert sha(E/path)==row['sha256']
assert json.loads((A/'equivalence-gate-02.json').read_text())['pass_equivalence']
save(A/'smoke-gate.json',dict(utc=utc(),**{'pass':True},checks=checks,active_smoke='smoke-02',smoke_only_deviation='N plane, solid zone-pad connection; no added/renamed nets',main_reused_unchanged=True,router_settings_unchanged=True,stage1_allowed=True,initial_smoke_attempt_preserved=True))
print('SMOKE GATE PASS',utc())
