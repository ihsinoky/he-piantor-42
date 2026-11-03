"""Recheck saved Freerouting comparison artifacts without executing old workflows."""
import hashlib,json,pathlib,re
E=pathlib.Path(__file__).resolve().parent; base=E.parents[1]; results=[]
comparison=json.loads((E/'freerouting-comparison-source.json').read_text())
for issue,run,key in [('issue-93-freerouting-v250-jar','run-1','run1'),('issue-95-freerouting-v250-run2','run-2','run2')]:
    d=base/issue/'evidence/processes'/run; record=json.loads((d/'record.json').read_text())
    for f,h in record['artifacts'].items(): assert hashlib.sha256((d/f).read_bytes()).hexdigest()==h
    events=re.findall(r'Auto-routing pass #(\d+).*?was completed.*?\((\d+) unrouted',(d/'stdout').read_text())
    assert len(events)==comparison[key]['completed_passes']==18
    assert min(int(x[1]) for x in events)==comparison[key]['best_pass_unrouted']
    results.append(dict(issue=issue,record_sha256=hashlib.sha256((d/'record.json').read_bytes()).hexdigest(),all_artifact_hashes_match=True,elapsed_seconds=record['elapsed_seconds'],exit_code=record['exit_code'],completed_pass_events=len(events),pass_events=events))
(E/'baseline-verification.json').write_text(json.dumps(results,indent=2)+'\n'); print('Baseline hashes and pass summaries match')
