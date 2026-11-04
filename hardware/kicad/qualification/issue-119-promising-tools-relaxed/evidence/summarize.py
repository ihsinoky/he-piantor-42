from common import *
import re,collections
cells={'A':('main4','fab'),'B':('main4','krt'),'C':('main4','free'),'D':('main2','fab')}
def endpoints(drc):
 rows=[];nets=collections.Counter();refs=collections.Counter();u1=0
 for row in drc['unconnected_items']:
  names={m for item in row['items'] for m in re.findall(r'\[([^]]+)\]',item['description'])};assert len(names)==1,names
  net=next(iter(names));nets[net]+=1
  named_refs={m for item in row['items'] for m in re.findall(r' of ([^ ]+) on ',item['description'])}
  refs.update(named_refs);u1+=('U1' in named_refs)
  rows.append(dict(net=net,items=row['items'],explicit_pad_refs=sorted(named_refs)))
 return dict(missing_connections=len(rows),by_net=dict(sorted(nets.items())),rows=rows,explicit_pad_reference_missing_rows=dict(refs),rows_explicitly_touching_U1_pad=u1,definition='Counts KiCad missing-connection rows with a literal Pad ... of U1 endpoint. Tracks/vias may connect to U1 indirectly; not assigned to a component by proximity.')
results={}
for cell,(label,router) in cells.items():
 w=E/'inspection'/label/router;d=json.loads((w/'independent.json').read_text());drc=json.loads((w/'drc.json').read_text());ends=endpoints(drc);save(w/'unconnected-net-endpoints.json',ends)
 rec=json.loads((E/'processes'/(label+'-'+router+'-route')/'record.json').read_text());raw=E/'runs'/label/router
 if router=='fab':
  self_report=json.loads((raw/'result.json').read_text())['report'];stop=self_report.get('stoppedBy');self_counts=json.loads((raw/'check-drc-after.json').read_text())['counts']
 elif router=='free':
  lines=(raw/'user-data/freerouting.log').read_text().splitlines()
  selected=[dict(line=i,text=line) for i,line in enumerate(lines,1) if any(s in line for s in ['Applied CLI router setting:','Pipeline thread limits:','settings.fanout.enabled','Fanout stage','fanout stage','Skipping optimization','optimization stage','Set DEFAULT clearance','Set default trace width','Layer 1:','Analytics are disabled','Merging settings','Settings merged',' - API Settings','Auto-routing pass #','Restor','Final','final','completed','stagn','unchanged','settings.optimizer.enabled'])]
  save(raw/'effective-settings-readback.json',dict(events=selected,saved_json_scope='freerouting.json contains pre-CLI defaults, not an effective job dump',readback_limits='-is final selection and all internal scoring settings are not directly dumped. Runtime flags, fanout behavior, thread count and optimizer behavior come from log. Nominal mm rendering in startup is inconsistent with DSN units; independently imported widths measured separately.',input_dimensions_um=dict(width=127,clearance=127,via=600,drill=300)))
  last=[line for line in lines if 'unrouted' in line or 'unconnected' in line];self_counts=dict(final_log_lines=last[-6:]);self_report={};stop='; '.join(line for line in lines if 'stagn' in line.lower() or 'improv' in line.lower() and ('stop' in line.lower() or 'consecutive' in line.lower()))
 else:
  lines=(E/'processes'/(label+'-'+router+'-route')/'stdout').read_text().splitlines();self_counts={tag:json.loads(next(line.split(tag+': ',1)[1] for line in reversed(lines) if line.startswith(tag+': '))) for tag in ['JSON_REGRADE','JSON_SUMMARY_MIN']};self_report={};stop='Fixed CLI completed routing, rescue, reconciliation and re-grade; inspect final stdout for self grading.'
 results[cell]=dict(label=label,router=router,measured_unconnected_count=d['measured_unconnected_count'],metrics=d['metrics'],pass_acceptance=d['pass_acceptance'],physical=d['physical'],unconnected_distribution=ends,raw_DRC_type_counts=d['drc_type_counts'],raw_material_DRC_count=d['raw_material_DRC_count'],raw_short_DRC_count=d['raw_short_DRC_count'],raw_unexplained_transfer_count=d['unexplained_change_raw_count'],project_diff=d['output_project_changes'],router_self_counts=self_counts,router_report=self_report,stop_reason=stop,execution=rec)
prior={}
for router in ['fab','krt']:
 w=E/'source-117/amendment-01/inspection/main'/router;prior[router]=endpoints(json.loads((w/'drc.json').read_text()))
save(E/'assessment.json',dict(utc=utc(),cells=results,comparison117=prior,all_main_routers_run_once=True,independent_DRC_executed_for_incomplete_boards=True,decision='PASS' if any(d['pass_acceptance'] for d in results.values()) else 'FIXED_CONDITION_FAIL',null_semantics='Any residual unconnected items: all four qualification metrics null, while raw DRC, transfer and physical observations remain saved.'))
print(json.dumps({c:dict(unconnected=d['measured_unconnected_count'],metrics=d['metrics'],tracks=d['physical']['tracks_per_layer']) for c,d in results.items()},indent=2))
