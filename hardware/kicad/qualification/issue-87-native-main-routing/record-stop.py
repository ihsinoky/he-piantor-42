"""Fail closed on the raw public export's effective typed clearance."""
from prepare import *
import re,collections
# Reconfirm immutable input bytes; never invoke historical frontend/router drivers.
inputs=json.loads((OLD.parent/'evidence/input-freeze.json').read_text())
checks={}
for path in ['src/qualification/revm1-routing-proof.tsx','src/qualification/JstGh14.tsx','src/qualification/native-support-footprints.tsx','src/components/HallKey.tsx','qualification/eda-003c/latest-stock/package-lock.json']:
    p=REPO/'hardware/tscircuit'/path
    original=subprocess.check_output(['git','show','b84585ecc2cf32000285bbf389d9fea255436980:hardware/tscircuit/'+path],cwd=REPO)
    assert hashlib.sha256(original).hexdigest()==digest(p)
    checks[str(p.relative_to(REPO))]=digest(p)
save(ROOT/'evidence/immutable-inputs.json',checks)
results={}
for name in ['smoke','main']:
    p=BASE/name/'input.dsn';s=p.read_text()
    assert '(unit um)' in s and '(clearance 200)' in s
    typed=re.findall(r'\(clearance ([\d.]+) \(type ([^)]+)\)\)',s)
    assert ('50','smd_smd') in typed
    results[name]=dict(input_sha256=digest(p),ordinary_clearance_mm=.2,typed_clearances_mm={k:float(v)/1000 for v,k in typed},status='FAIL_RULE_TRANSFER',ses=None,router_launched=False,individual_DSN_geometry_reconciliation='NOT_COMPLETED: rule prerequisite fails first')
source=(ROOT/'evidence/specctra_export.cpp').read_text();assert 'clearance = scale( defaultClearance ) / 4;' in source
global_source=(ROOT/'evidence/GlobalSettings.java').read_text();assert 'Its function is now removed, .rules files are considered to be deprecated' in global_source
settings=(ROOT/'evidence/RouterSettings.java').read_text();assert 'clearance' not in settings.lower()
save(ROOT/'evidence/transfer-rule-check.json',dict(result='FAIL_RULE_TRANSFER',exports=results,public_export_signatures='processes/pcbnew-probe/stdout',official_export_source='specctra_export.cpp:1151',official_override_limit='GlobalSettings.java:75-79 (.rules function removed); InitializeCLI only copies RouterSettings, whose public configuration has no clearance override',bounds='No claim of exhaustive API impossibility; no DSN editing, router internals, different version, rule relaxation or speculative -dr invocation used.'))
stop=utc()
save(ROOT/'evidence/attempt-ledger.json',dict(initial=0,confirmation=0,small_roundtrip=0,dsn_exports=2,small_preparation_create_failures=1,router_help=1,main_metrics=None,confirmation_metrics=None,small_roundtrip_result='NOT_ENTERED; raw DSN rule prerequisite failed before router launch'))
save(ROOT/'evidence/stop-decision.json',dict(utc=stop,classification='CONVERSION_BLOCKED / DSN_RULE_TRANSFER_UNQUALIFIED / MAIN_UNQUALIFIED',first_terminal_gate='C: public KiCad DSN export material-rule reconciliation',reason='Both smoke and Main raw DSN lower typed smd_smd clearance from required 0.20mm to 0.05mm. KiCad 9.0.9 hardcodes /4; documented Freerouting 2.1.0 -dr option is deprecated with function removed in its own source, and inspected public RouterSettings has no clearance override. A supported fixed-rule handoff has not been established within the evaluated public API/configuration path.',experiment_restart_forbidden=True,not_method_wide_failure=True,after_stop='record/report/verify-saved-evidence/commit/push/Draft PR/CI only'))
print(stop,'STOP; Main 0/0, transport 0; DSN exports only 2')
