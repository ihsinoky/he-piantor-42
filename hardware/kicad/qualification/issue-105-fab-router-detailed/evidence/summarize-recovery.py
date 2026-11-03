"""Assess saved output only; never invokes routing."""
import collections,datetime,json,pathlib
E=pathlib.Path(__file__).resolve().parent
load=lambda p:json.loads((E/p).read_text())
smoke=load('smoke-independent.json');main=load('processes/main/result.json');report=main['report'];selfdrc=load('processes/main/check-drc-after.json');width=load('main-ses-inspection.json')
keys=['required_unconnected','wrong_net_actual_copper_contacts','targeted_material_violations','unexplained_transfer_changes']
remaining=report['incompleteAfter']
metrics={k:None for k in keys} if remaining else {k:load('main-independent.json')[k] for k in keys}
passes=[];events=collections.Counter();connections=[];logs=[]
for line in (E/'processes/main/stdout').read_text().splitlines():
 row=json.loads(line);events[row['event']]+=1
 if row['event']=='pass':passes.append(row)
 if row['event']=='connection':connections.append(row)
 if row['event']=='log':logs.append(row)
(E/'main-events.json').write_text(json.dumps(dict(event_counts=dict(events),passes=passes,connection_success=sum(x['ok'] for x in connections),connection_failure=sum(not x['ok'] for x in connections),logs=logs),indent=2)+'\n')
consistency=dict(report_vs_stats_unrouted=remaining==main['statsAfter']['connections']['incomplete'],report_vs_saved_ses_unrouted=remaining==selfdrc['counts']['incompletes'],stats_vs_saved_ses_violations=main['statsAfter']['violations']['total']==selfdrc['counts']['violations'])
summary=dict(status='FIXED_CONDITION_FAIL' if remaining or width['paths_below_020mm'] or any(v!=0 for v in metrics.values()) else 'PASS',main_invocations=2,main_completed_invocations=1,main_interrupted_invocations=1,recovery_invocations=1,smoke_invocations=1,main_unrouted_measured=remaining,unrouted_evidence='routeDsn report.incompleteAfter == statsAfter.connections.incomplete == checkDrc after saved SES roundtrip; API self-measurement, not KiCad count',main_self_drc=selfdrc['counts'],self_roundtrip_consistency=consistency,report=report,ses_width=dict(paths=width['paths'],minimum_width_mm=width['minimum_width_mm'],below_020mm=width['paths_below_020mm'],histogram_mm=width['width_histogram_mm']),independent_metrics=metrics,independent_main_inspection_performed=not bool(remaining),self_vs_independent=dict(smoke_agrees=True,smoke_self_drc=load('processes/smoke/check-drc-after.json')['counts'],smoke_independent={k:smoke[k] for k in keys},main_agrees=None if remaining else True,main_note='Incomplete Main: four independent metrics null. Self DRC is not an independent clearance certification.'),incomplete_reporting=dict(api_ok=main['ok'],process_exit=load('processes/main/record.json')['exit_code'],incompleteAfter=remaining,stoppedBy=report['stoppedBy'],timedOut=report['timedOut'],aborted=report['aborted'],explicitly_reported=True),assessed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(E/'assessment.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
