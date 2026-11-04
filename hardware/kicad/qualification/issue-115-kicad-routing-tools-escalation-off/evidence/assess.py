"""Summarize independent measurements and compare exact DRC-open net sets."""
import runpy,re,collections
from pathlib import Path
E=Path(__file__).resolve().parent;globals().update(runpy.run_path(str(E/'prepare-inputs.py')))
prior=R/'hardware/kicad/qualification/issue-113-kicad-routing-tools-falsification/evidence'
def nets(d):
 out=collections.Counter()
 for row in d['unconnected_items']:
  ns={re.search(r'\[([^]]+)\]',x['description']).group(1) for x in row['items']}
  assert len(ns)==1,ns
  out[next(iter(ns))]+=1
 return dict(sorted(out.items()))
drc=json.loads((E/'inspection/main/drc.json').read_text());prev=json.loads((prior/'inspection/main/drc-with-library.json').read_text());current=nets(drc);before=nets(prev)
assert not any(v['type']=='lib_footprint_issues' for v in drc['violations'])
rows={}
for stage in ['smoke','main']:
 diff=json.loads((E/f'{stage}-board-diff.json').read_text());width=json.loads((E/f'{stage}-width-inspection.json').read_text());a=json.loads((E/f'{stage}-independent.json').read_text())
 changes=diff['output_project_changes'];floors=[x for x in changes if len(x['path'])>=4 and x['path'][:3]==['board','design_settings','rules'] and x['path'][3].startswith('min_')]
 rows[stage]=dict(independent=a['metrics'],measured_unconnected_items=a['measured_kicad_unconnected_items'],tracks=width['tracks'],width_mm_counts=width['width_mm_counts'],minimum_track_width_mm=width['minimum_mm'],below_020=width['below_020'],vias=width['vias'],nonroute_removed=len(diff['nonroute_removed']),nonroute_added=len(diff['nonroute_added']),source_routes_removed=len(diff['source_route_records_removed']),snapshot_nonroute_changes=diff['snapshot_nonroute_changes'],output_project_changes=changes,output_project_floor_writebacks=floors,existing_floor_relaxations=[x for x in floors if x['kind']=='changed' and x['after']<x['before']],output_sha256=digest(E/f'runs/{stage}/out.kicad_pcb'),route_record=json.loads((E/f'processes/{stage}-route/record.json').read_text()))
main=rows['main'];reasons=[]
if main['measured_unconnected_items']:reasons.append('unconnected items remain')
if main['below_020']:reasons.append('tracks below 0.20mm')
if main['nonroute_removed'] or main['nonroute_added'] or main['source_routes_removed'] or main['snapshot_nonroute_changes']:reasons.append('unexplained PCB transfer changes')
if main['output_project_floor_writebacks']:reasons.append('output project minimum rule writeback (including additions)')
if any(v not in [0,None] for v in main['independent'].values()):reasons.append('nonzero independent metrics')
save(E/'assessment.json',dict(verdict='FIXED_CONDITION_FAIL' if reasons else 'PASS',failure_reasons=reasons,stages=rows,main_drc_type_counts=dict(collections.Counter(x['type'] for x in drc['violations'])),unconnected_comparison=dict(issue115_net_item_counts=current,issue113_net_item_counts=before,common=sorted(set(current)&set(before)),new=sorted(set(current)-set(before)),resolved=sorted(set(before)-set(current)),issue113_net_set_is_subset=set(before)<=set(current)),note='Unconnected counts are DRC missing-connection items, not distinct nets; all four Main metrics null whenever any open remains. Any min_* addition is disclosed as writeback; unchanged existing numeric floors do not establish no-writeback.'))
print(json.dumps(dict(verdict='FIXED_CONDITION_FAIL' if reasons else 'PASS',reasons=reasons,unconnected=current,widths=main['width_mm_counts'],floor_writebacks=main['output_project_floor_writebacks']),indent=2))
