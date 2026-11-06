"""Seal every tested candidate and select the first collision-free native preflight."""
from common import *
import shutil,collections
ignored={'text_height','silk_overlap','silk_over_copper','via_dangling'}
rows=[]
for w in sorted((E/'inputs').glob('candidate-*')):
 if not (w/'main.kicad_pcb').exists():continue
 d=w/'preflight.json';data=json.loads(d.read_text());bad=[v for v in data['violations'] if v['type'] not in ignored]
 row=dict(candidate=w.name,utc=now(),board_sha256=digest(w/'main.kicad_pcb'),project_sha256=digest(w/'main.kicad_pro'),drc_sha256=digest(d),pass_preflight=not bad,blocking_violations=bad,type_counts=dict(collections.Counter(v['type'] for v in data['violations'])),expected_unrouted_connections=len(data['unconnected_items']),ignored_print_and_pre_route_via_warnings=sorted(ignored))
 save(w/'preflight-receipt.json',row);rows.append(row)
assert len(rows)<=3
chosen=next(r for r in rows if r['pass_preflight']);shutil.copytree(E/'inputs'/chosen['candidate'],E/'inputs/final');shutil.copyfile(E/'inputs/final/preflight.json',E/'preflight.json');save(E/'preflight-receipt.json',chosen)
save(E/'candidate-selection.json',dict(utc=now(),candidate_count=len(rows),max_candidates=3,selected=chosen['candidate'],attempts=rows))
save(E/'routing-scope.json',dict(utc=now(),max_global_attempts=1,max_local_repair_attempts=0,timeout_seconds=2400,condition_args=ARGS+['--keep-input-copper'],ordering='mps (default)',direction='default',no_condition_relaxation=True))
print('Selected',chosen['candidate'])
