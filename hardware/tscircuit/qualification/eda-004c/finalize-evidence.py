"""Records/manifest preparation only; never starts an EDA process."""
from process import *
import subprocess
REPO=ROOT.parents[3]
start=datetime.datetime.fromisoformat('2026-10-08T11:09:00+00:00')
now=datetime.datetime.now(datetime.timezone.utc)
prior=json.loads((ROOT.parent/'eda-004b/evidence/effort-ledger.json').read_text())
observed=(now-start).total_seconds()/3600
estimate=max(.75,round(observed+.15,3))
known=round(estimate+prior['engineer_hours_estimate_upper_bound'],3)
save(EVIDENCE/'effort-ledger.json',{'operator':'Codex / AI session','start_utc_estimate':start.isoformat(),'first_exact_clock_observation_utc':json.loads((EVIDENCE/'preflight.json').read_text())['observed_utc'],'recorded_utc':now.isoformat(),'elapsed_session_hours_estimate_at_record':observed,'issue_ai_hours_estimate':estimate,'estimate_basis':'Conservative continuous-session allowance including reporting, validation, commit/push, CI and PR completion reserve; not measured active engineer-hours. Finish rechecked against this allowance in final PR body.','issue_cap_hours':4,'prior_eda004b_reported_ai_hours_estimate':prior['engineer_hours_estimate_upper_bound'],'prior_reference':'EDA-004B effort-ledger.json and saved final PR #74 body','prior_unquantified_effort':'Later historical reporting/review correction and human effort not quantified; not assumed zero.','known_cumulative_ai_hours_estimate':known,'original_cap_hours':16,'nominal_remaining_hours_from_known_estimates':round(16-known,3),'exact_remaining_engineer_hours':None,'remaining_limit':'Nominal remainder excludes unobserved prior correction/human effort; exact total/remaining cannot be certified. No budget reset.','human_active_hours':None,'measured_engineer_hours':None,'unattended_process_elapsed_seconds':None,'process_elapsed_reference':'process-summary.json; observed process elapsed overlaps AI work, not added as engineer-hours or claimed fully unattended.','checkpoints':[{'task':'preflight/protection/authority/process control','status':'complete with disclosed correction'},{'task':'regular source build/isolated fixed-pinned setup','status':'build and probes passed; complete library/rule environment not qualified'},{'task':'fixture/raw/input reconciliation/conversion','status':'terminal conversion STOP'},{'task':'DSN/route/fresh confirmation','status':'NOT ENTERED'},{'task':'report/validation/commit/push/PR/CI','status':'included in current estimate/reserve'}]})
protected=json.loads((EVIDENCE/'protected-start.json').read_text())
end={p:digest(REPO/p) for p in protected}
assert end==protected
save(EVIDENCE/'protected-end.json',{'recorded_utc':utc(),'sha256':end,'byte_hash_match':True,'protected_file_count':len(end)})
# Evidence CI snapshot can precede final HEAD; live final-HEAD check is in PR body.
if not (EVIDENCE/'ci-record.json').exists():
 save(EVIDENCE/'ci-record.json',{'status':'PENDING','final_head_check_location':'PR #76 final body','note':'Current HEAD must be checked after the final evidence commit; CI is PR hygiene, not EDA qualification.'})
exclude={'evidence/artifact-manifest.json','evidence/validation.json','evidence/ci-record.json','evidence/effort-ledger.json','evidence/protected-end.json'}
manifest={}
for p in sorted(ROOT.rglob('*')):
 relative=str(p.relative_to(ROOT))
 if not p.is_file() or relative in exclude or '__pycache__' in p.parts:continue
 if relative.startswith('evidence/processes/validation-') or relative.startswith('evidence/processes/pr-management-'):continue
 manifest[relative]={'sha256':digest(p),'bytes':p.stat().st_size}
save(EVIDENCE/'artifact-manifest.json',manifest)
print(json.dumps({'protected':len(end),'artifacts':len(manifest),'estimated_issue_hours':estimate,'known_cumulative_hours':known,'nominal_remaining_hours':16-known}))
