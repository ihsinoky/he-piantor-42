#!/usr/bin/env python3
"""Read saved evidence only; never launches router or changes older evidence."""
import collections,csv,hashlib,json,pathlib,re,subprocess
E=pathlib.Path(__file__).resolve().parent
R=E.parents[4]
P=E/'processes/run-2'
ref='b2ed21437428ba975c0519734da6cb5ed57522bc'
oldroot='hardware/kicad/qualification/issue-93-freerouting-v250-jar/evidence/'
def summarize(text,record,label):
 rows=[dict(pass_number=int(m[1]),unrouted=int(m[2]),violations=int(m[3]) if m[3] else None,log_line=m[0]) for m in re.finditer(r'Auto-rout(?:er|ing) pass #(\d+).*?completed.*?\((\d+) unrouted(?: and (\d+) violations)?\)',text)]
 with (E/(label+'-pass-history.csv')).open('w') as f:
  w=csv.DictWriter(f,fieldnames=['pass_number','unrouted','violations','log_line'],lineterminator='\n');w.writeheader();w.writerows(rows)
 lines=text.splitlines();errors=[(i,l) for i,l in enumerate(lines) if re.search(r'\bERROR\b',l)]
 def types(events):
  return dict(collections.Counter(next((t for t in ('NullPointerException','ArrayIndexOutOfBoundsException') if t in l+' '+(lines[i+1] if i+1<len(lines) else '')),'other_ERROR') for i,l in events))
 maze=[(i,l) for i,l in errors if 'Exception in maze_search_algo.find_connection' in l]
 stage=re.findall(r'Auto-routing stage completed:.*?\((\d+) unrouted',text)
 best=min((r['unrouted'] for r in rows),default=None)
 return dict(completed_passes=len(rows),last_pass=rows[-1]['pass_number'] if rows else None,best_pass_unrouted=best,first_best_pass=next((r['pass_number'] for r in rows if r['unrouted']==best),None),last_pass_unrouted=rows[-1]['unrouted'] if rows else None,autorouter_final_unrouted=int(stage[-1]) if stage else None,maze_exception_events=len(maze),maze_exception_types=types(maze),stdout_ERROR_events=len(errors),error_types=types(errors),elapsed_seconds=record['elapsed_seconds'],exit_code=record['exit_code'],timed_out=record['timed_out'])
b=R/'hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/processes/main-initial-route'
brec=json.loads((b/'record.json').read_text())
# Raw legacy logs remain read-only, and their recorded digest is verified below.
assert hashlib.sha256((b/'stdout').read_bytes()).hexdigest()==brec['stdout_sha256']
assert hashlib.sha256((b/'stderr').read_bytes()).hexdigest()==brec['stderr_sha256']
btext=(b/'stdout').read_text()
baseline=summarize(btext,brec,'baseline-v210')
oldtext=subprocess.check_output(['git','show',ref+':'+oldroot+'processes/run-1/stdout'],text=True)
oldrec=json.loads((E/'reference/run-1-record.json').read_text())
assert hashlib.sha256(oldtext.encode()).hexdigest()==oldrec['artifacts']['stdout']
run1=summarize(oldtext,oldrec,'run-1')
record=json.loads((P/'record.json').read_text());assert 'end_utc' in record,'Run is still active'
text=(P/'stdout').read_text();detail=(P/'user-data/freerouting.log').read_text();stderr=(P/'stderr').read_text()
run2=summarize(text,record,'run-2')
run2['stderr_bytes']=len((P/'stderr').read_bytes())
run2['stderr_exception_lines']=[l for l in stderr.splitlines() if re.search(r'Exception|Error',l)]
run2['detail_exception_lines']=[dict(line=i,text=l) for i,l in enumerate(detail.splitlines(),1) if re.search(r'Exception|\bERROR\b',l)]
run2['stop_reason']=[l for l in text.splitlines() if 'Stopping the auto-router' in l]
run2['fanout_completed_passes']=len(re.findall(r'Fanout pass #\d+.*?completed',text))
run2['fanout_stage']=[l for l in text.splitlines() if 'Fanout stage completed:' in l]
run2['optimizer_enabled_cli']='Applied CLI router setting: router.optimizer.enabled = true' in detail
run2['optimizer_executed']=False if 'Skipping optimization stage:' in text else None
run2['optimizer_skip_reason']=[l for l in text.splitlines() if 'Skipping optimization stage:' in l]
run2['final_unrouted']=run2['autorouter_final_unrouted'] if run2['optimizer_executed'] is False else None
pattern=r'Fanout|fanout pre-pass|Optimization|Optimiz|optimizer|Auto-routing stage|stagnat|best board|best score|COMPLETED|TIMED_OUT|Session|SES|unrouted|Analytics are disabled'
events=[dict(line=i,text=l) for i,l in enumerate(detail.splitlines(),1) if re.search(pattern,l)]
(E/'stage-events.json').write_text(json.dumps(events,indent=2)+'\n')
(E/'summary.json').write_text(json.dumps(dict(baseline_v210=baseline,run1=run1,run2=run2),indent=2)+'\n')
print(json.dumps(run2,indent=2))
