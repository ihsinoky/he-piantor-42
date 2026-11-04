"""Read saved KiCad results; raw diagnostic counts never substitute for acceptance."""
import collections,datetime,importlib.util,json,pathlib,sys
import sexpdata as sx
E=pathlib.Path(__file__).resolve().parent; ROOT=E.parents[4];stage=sys.argv[1]
old=ROOT/'hardware/kicad/qualification/issue-87-native-main-routing/evidence/processes'/('smoke-read-before' if stage=='smoke' else 'baseline-read');work=E/'processes'/(stage+'-import')
spec=importlib.util.spec_from_file_location('checker',ROOT/'hardware/kicad/qualification/issue-87-native-main-routing/check-main.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
a=json.loads((old/'snapshot.json').read_text());b=json.loads((work/'snapshot.json').read_text());d=json.loads((work/'drc.json').read_text())
def nonroute(p):
 t=sx.loads(p.read_text());return collections.Counter(sx.dumps(x) for x in t[1:] if not isinstance(x,list) or not x or str(x[0]) not in ['segment','via'])
graph=m.snapshot_graph(b);printing={'text_height','silk_overlap','silk_over_copper'}
raw=dict(kicad_unconnected_items=len(d['unconnected_items']),kicad_violations=len(d['violations']),kicad_violation_types=dict(collections.Counter(v['type'] for v in d['violations'])),nonprinting_violations=sum(v['type'] not in printing for v in d['violations']),graph=graph,wrong_net_contact_pairs=len(graph['shorts']),nonroute_semantics_identical=nonroute(old/'main.kicad_pcb')==nonroute(work/'main.kicad_pcb'),snapshot_nonroute_identical=all(a[k]==b[k] for k in a if k!='tracks'),original_tracks=len(a['tracks']),returned_tracks=len(b['tracks']))
from shapely.geometry import LineString
from shapely.ops import unary_union
local=[]
for t in a['tracks']:
 source=LineString([t['start'],t['end']]);candidates=[x for x in b['tracks'] if x['kind']=='track' and all(x[k]==t[k] for k in ['width','net','layer'])]
 missing=source.difference(unary_union([LineString([x['start'],x['end']]) for x in candidates])).length
 local.append(dict(source=t,missing_centerline_length_mm=missing,preserved=missing<=m.C['tolerance_mm']))
raw.update(source_local_copper=local,source_local_copper_preserved=all(x['preserved'] for x in local),before_graph=m.snapshot_graph(a))
rec=json.loads((E/'processes'/stage/'record.json').read_text());width=json.loads((E/(stage+'-ses-inspection.json')).read_text())
keys=['required_unconnected','wrong_net_actual_copper_contacts','targeted_material_violations','unexplained_transfer_changes']
passed=rec['exit_code']==0 and not rec['outer_timeout'] and not raw['kicad_unconnected_items'] and not raw['nonprinting_violations'] and not graph['shorts'] and not graph['disconnected'] and raw['nonroute_semantics_identical'] and raw['snapshot_nonroute_identical'] and raw['source_local_copper_preserved'] and not width['paths_below_020mm']
# A PASS must additionally have actually executed the unchanged independent oracle.
check=json.loads((E/'processes'/(stage+'-independent')/'record.json').read_text());passed=passed and check['exit_code']==0
metrics={k:0 if passed else None for k in keys}
result=dict(status='PASS' if passed else 'FIXED_CONDITION_FAIL',router_exit_code=rec['exit_code'],unrouted_count=raw['kicad_unconnected_items'],unrouted_count_method='len(unconnected_items) from KiCad DRC JSON after importing saved SES into original board copy; not router failed-net count or endpoint deficit.',four_metrics=metrics,diagnostic_only=raw,oracle_exit_code=check['exit_code'],oracle_stderr=(E/'processes'/(stage+'-independent')/'stderr').read_text(),elapsed_seconds=rec['elapsed_seconds'],null_reason=None if passed else 'Stage failed; raw diagnostics are not acceptance metrics. Exit 2 explicitly requires all four metrics null.',measured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(E/(stage+'-measurement.json')).write_text(json.dumps(result,indent=2)+'\n')
if stage=='smoke':
 (E/'smoke-gate.json').write_text(json.dumps(dict(main_allowed=passed,headless_exit_zero=rec['exit_code']==0,ses_generated=rec['ses_exists'],kicad_import_success=True,independent_checks_passed=passed,unrouted_count=result['unrouted_count'],reason='All smoke gates passed' if passed else 'Stage 0 failed: Main forbidden'),indent=2)+'\n')
print(json.dumps(result,indent=2))
