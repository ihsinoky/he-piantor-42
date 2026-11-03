"""Summarize immutable router logs; parallel variant events retain no invented identity."""
import csv,hashlib,json,pathlib,re
E=pathlib.Path(__file__).resolve().parent; work=E/'processes/main'
record=json.loads((work/'record.json').read_text()); assert 'end_utc' in record
log=(work/'stderr').read_text(); lines=log.splitlines(); report=json.loads((work/'report.json').read_text())
pattern=re.compile(r'^\s*([\d.]+) INFO  Auto-routing pass #(\d+) was completed in ([\d.]+) seconds with score ([\d.]+) \((\d+) unrouted and (\d+) violations\)')
passes=[]; events=[]; first_stage_end=None
for i,line in enumerate(lines,1):
    m=pattern.search(line)
    if m:
        stamp,p,seconds,score,unrouted,violations=m.groups()
        passes.append(dict(line=i,elapsed_s=float(stamp),pass_number=int(p),pass_seconds=float(seconds),score=float(score),unrouted=int(unrouted),violations=int(violations),scope='first run' if first_stage_end is None else 'parallel variants (identity not logged)'))
    if 'Auto-routing stage completed:' in line and first_stage_end is None: first_stage_end=i
    if any(s in line for s in ['stage started','stage completed','checkpoint:','Multi-start','Optimization','optimization','Optimizer','optimizer','stop','Stopping','restor','WARN','ERROR','panic','saved ','report written']): events.append(dict(line=i,text=line))
with (E/'main-pass-history.csv').open('w') as f:
    writer=csv.DictWriter(f,fieldnames=list(passes[0]),lineterminator='\n'); writer.writeheader(); writer.writerows(passes)
(E/'stage-events.json').write_text(json.dumps(events,indent=2)+'\n')
primary=[p for p in passes if p['scope']=='first run']
summary=dict(router_invocations=dict(smoke=1,main=1),exit_code=record['exit_code'],elapsed_seconds=record['elapsed_seconds'],outer_timeout=record.get('outer_timeout',False),final_unrouted=report['stats']['unrouted'],final_clearance_violations=report['stats']['violations'],first_run_completed_passes=len(primary),first_run_last_pass=primary[-1]['pass_number'],first_run_best_pass_unrouted=min(p['unrouted'] for p in primary),autorouter_completed_pass_events_all_runs=len(passes),parallel_variant_completed_pass_events=len(passes)-len(primary),parallel_variant_identity_limitation='Concurrent logs have no variant labels on pass lines; do not reconstruct per-variant histories.',autorouter_stage_completions=[dict(line=i,text=l) for i,l in enumerate(lines,1) if 'Auto-routing stage completed:' in l],multi_start=[dict(line=i,text=l) for i,l in enumerate(lines,1) if 'Multi-start' in l],warning_lines=[dict(line=i,text=l) for i,l in enumerate(lines,1) if ' WARN ' in l],error_lines=[dict(line=i,text=l) for i,l in enumerate(lines,1) if ' ERROR ' in l],exception_or_panic_lines=[dict(line=i,text=l) for i,l in enumerate(lines,1) if re.search(r'panic|exception|backtrace',l,re.I)],scope='Count of observed panic/exception diagnostics only; no claim about unlogged internally handled failures or equivalence to Java exception classes.',optimizer_stage_lines=[dict(line=i,text=l) for i,l in enumerate(lines,1) if any(s in l for s in ['Optimization stage', 'Optimizer pass #', 'Optimizer time budget'])],report_stats=report['stats'])
(E/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
