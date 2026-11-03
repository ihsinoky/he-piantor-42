"""Aggregate saved evidence only; never starts a router."""
import csv,hashlib,json,pathlib,re
root=pathlib.Path(__file__).resolve().parent
old=root.parents[1]/'issue-87-native-main-routing/resume-01/evidence'
run=root/'processes/run-1'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pattern=re.compile(r'Auto-router pass #(\d+).*?completed.*?\((\d+) unrouted\)')
def samples(p):
 return [{'pass':int(m[1]),'unrouted':int(m[2])} for m in pattern.finditer(p.read_text())]
a=samples(old/'processes/main-initial-route/stdout'); b=samples(run/'stdout')
assert len(a)==512 and a[-1]=={'pass':512,'unrouted':36}
assert min(x['unrouted'] for x in a)==35
assert not b
old_errors=(old/'processes/main-initial-route/stdout').read_text().count('ERROR  AutorouteEngine.autoroute_connection: Exception in maze_search_algo.find_connection')
assert old_errors==371
stderr=(run/'stderr').read_text();assert stderr.count('Exception in thread "Thread-1"')==1 and 'UnsupportedFeatureError' in stderr
record=json.loads((run/'record.json').read_text())
summary={'baseline_v210':{'completed_passes':len(a),'last_completed_pass':a[-1]['pass'],'best_unrouted':35,'first_best_pass':next(x['pass'] for x in a if x['unrouted']==35),'final_pass_unrouted':36,'maze_exception_count':old_errors,'elapsed_seconds':1203.7524132630006,'exit_code':0},'run_1_v250':{'completed_passes':len(b),'last_completed_pass':None,'best_unrouted':None,'final_unrouted':None,'maze_exception_log_count':0,'maze_exception_zero_is_resolution':False,'uncaught_fatal_errors':{'com.oracle.svm.core.jdk.UnsupportedFeatureError: ObstacleArea serialization constructor missing':1},'elapsed_seconds':record['elapsed_seconds'],'exit_code':record['exit_code'],'natural_exit_code':None,'worker_terminated':True,'ses_present':(run/'output.ses').exists(),'result_manifest_present':(run/'result.json').exists(),'runtime_effective_settings_verified':False},'assessment':{'A':'判定不能','B':'判定不能','C':'判定不能'},'physical_metrics':{'required_unconnected':None,'wrong_net_contact':None,'target_material_violations':None,'unexplained_handoff_changes':None}}
(root/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
with (root/'baseline-pass-history.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=['pass','unrouted'],lineterminator='\n');w.writeheader();w.writerows(a)
(root/'run-2-gate.json').write_text(json.dumps({'authorized':False,'executed':False,'reason':'Run 1 fatal error before completed pass; pass-cap effectiveness and exception resolution unproven; no measured unrouted value. No retry or JAR fallback within this issue.'},indent=2)+'\n')
start=json.loads((root/'start.json').read_text())
assert all(h(pathlib.Path(p))==digest for p,digest in start['prior_evidence_hashes'].items())
(root/'integrity.json').write_text(json.dumps({'prior_evidence_hashes_unchanged':True,'files':{str(p.relative_to(root)):h(p) for p in sorted(root.rglob('*')) if p.is_file() and p.name!='integrity.json'}},indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
