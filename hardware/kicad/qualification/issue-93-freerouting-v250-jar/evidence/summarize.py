#!/usr/bin/env python3
"""Recompute pass histories from immutable raw stdout (do not double-count file log)."""
import collections,csv,hashlib,json,pathlib,re
E=pathlib.Path(__file__).resolve().parent;R=E.parents[4]
BASE=R/'hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/processes/main-initial-route'

def summarize(p,label):
 text=(p/'stdout').read_text();stderr=(p/'stderr').read_text();record=json.loads((p/'record.json').read_text())
 if 'end_utc' not in record:raise RuntimeError(f'{label} still running')
 pattern=r'Auto-rout(?:er|ing) pass #(\d+).*?completed.*?\((\d+) unrouted(?: and (\d+) violations)?\)'
 history=[dict(pass_number=int(m[1]),unrouted=int(m[2]),violations=int(m[3]) if m[3] else None,log_line=m[0]) for m in re.finditer(pattern,text)]
 with (E/(label+'-pass-history.csv')).open('w') as f:
  w=csv.DictWriter(f,fieldnames=['pass_number','unrouted','violations','log_line'],lineterminator='\n');w.writeheader();w.writerows(history)
 errors=[line for line in text.splitlines() if re.search(r'\bERROR\b',line)]
 maze_errors=[line for line in errors if 'Exception in maze_search_algo.find_connection' in line]
 # Each ERROR is one event, not every stack-frame occurrence of Exception.
 def count_types(events):
  counts=collections.Counter()
  lines=text.splitlines()
  for line in events:
   idx=lines.index(line)
   detail=line+' '+(lines[idx+1] if idx+1<len(lines) else '')
   kind=next((t for t in ('NullPointerException','ArrayIndexOutOfBoundsException') if t in detail),'other_ERROR')
   counts[kind]+=1
  return dict(counts)
 exception_types=count_types(errors)
 maze_types=count_types(maze_errors)
 best=min((h['unrouted'] for h in history),default=None)
 s=dict(completed_passes=len(history),last_completed_pass=history[-1]['pass_number'] if history else None,best_unrouted=best,first_best_pass=next((h['pass_number'] for h in history if h['unrouted']==best),None),final_pass_unrouted=history[-1]['unrouted'] if history else None,stdout_ERROR_events=len(errors),maze_exception_events=len(maze_errors),error_types=exception_types,maze_exception_types=maze_types,stderr_exception_line_count=sum(bool(re.search(r'Exception|Error',x)) for x in stderr.splitlines()),elapsed_seconds=record['elapsed_seconds'],exit_code=record['exit_code'],timed_out=record['timed_out'],ses_present=(p/'output.ses').exists() or (p/'output.ses.gz').exists(),samples={str(h['pass_number']):h['unrouted'] for h in history if h['pass_number'] in (1,2,5,10,25,50,75,100,200,201,300,400,500,512)},end_utc=record['end_utc'],final_stage_unrouted=(int(re.findall(r'Auto-routing stage completed:.*?\((\d+) unrouted',text)[-1]) if re.findall(r'Auto-routing stage completed:.*?\((\d+) unrouted',text) else None))
 return s

baseline=summarize(BASE,'baseline-v210');assert baseline['completed_passes']==512 and baseline['best_unrouted']==35 and baseline['maze_exception_events']==371
s={'baseline_v210':baseline}
for n in ['smoke','run-1','run-2']:
 p=E/'processes'/n
 if p.exists():s[n]=summarize(p,n)
(E/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
