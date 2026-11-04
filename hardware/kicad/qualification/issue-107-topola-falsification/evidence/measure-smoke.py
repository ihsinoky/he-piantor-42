"""Save terminal facts when the unmodified acceptance oracle stops at unconnected.
Diagnostic measurements do not replace the gated four acceptance metrics.
"""
import collections,datetime,hashlib,importlib.util,json,pathlib
import sexpdata as sx
E=pathlib.Path(__file__).resolve().parent;ROOT=E.parents[4]
old=ROOT/'hardware/kicad/qualification/issue-87-native-main-routing/evidence/processes/smoke-read-before'
work=E/'processes/smoke-import'
spec=importlib.util.spec_from_file_location('checker',ROOT/'hardware/kicad/qualification/issue-87-native-main-routing/check-main.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
a=json.loads((old/'snapshot.json').read_text());b=json.loads((work/'snapshot.json').read_text());d=json.loads((work/'drc.json').read_text())
def nonroute(p):
 t=sx.loads(p.read_text());return collections.Counter(sx.dumps(x) for x in t[1:] if not isinstance(x,list) or not x or str(x[0]) not in ['segment','via'])
def canonical(t):return json.dumps({k:v for k,v in t.items() if k!='uuid'},sort_keys=True)
graph=m.snapshot_graph(b)
raw=dict(kicad_unconnected_items=len(d['unconnected_items']),kicad_violations=len(d['violations']),graph=graph,nonroute_semantics_identical=nonroute(old/'main.kicad_pcb')==nonroute(work/'main.kicad_pcb'),snapshot_nonroute_identical=all(a[k]==b[k] for k in a if k!='tracks'),original_tracks=len(a['tracks']),returned_tracks=len(b['tracks']),returned_copper_equals_original=collections.Counter(map(canonical,a['tracks']))==collections.Counter(map(canonical,b['tracks'])))
metrics={k:None for k in ['required_unconnected','wrong_net_actual_copper_contacts','targeted_material_violations','unexplained_transfer_changes']}
result=dict(status='STAGE_0_FAIL_UNCONNECTED',unrouted_count=raw['kicad_unconnected_items'],unrouted_count_method='Number of unconnected_items in KiCad 9.0.9 DRC JSON after importing the saved SES into a copy of the original board. Not Topola self-report, endpoint deficit or disconnected-net count.',four_metrics=metrics,null_reason='Unrouted remains; all four acceptance metrics null per Issue #107 instructions.',diagnostic_only=raw,independent_acceptance_oracle=dict(script='issue-87-native-main-routing/resume-01/check-import.py',exit_code=1,failure='AssertionError: KiCad unconnected remains'),measured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(E/'smoke-independent.json').write_text(json.dumps(result,indent=2)+'\n')
(E/'smoke-gate.json').write_text(json.dumps(dict(main_allowed=False,headless_exit_zero=True,ses_generated=True,kicad_import_success=True,independent_checks_passed=False,unrouted_count=raw['kicad_unconnected_items'],reason='Stage 0 required unconnected remains; do not execute Main',validated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()),indent=2)+'\n')
(E/'assessment.json').write_text(json.dumps(dict(verdict='FIXED_CONDITION_FAIL',stage_0=result,stage_1=dict(status='NOT_RUN',attempts=0,reason='Stage 0 gate failed',unrouted_count=None,elapsed_seconds=None,ses_generated=None,four_metrics=metrics),settings_search=False,router_attempts=dict(smoke=1,main=0)),indent=2)+'\n')
print(json.dumps(result,indent=2))
