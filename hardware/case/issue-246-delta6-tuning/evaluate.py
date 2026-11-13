"""Retain the #244 gates, add the explicit 200 mm qualification constraint."""
import json
from pathlib import Path
H=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
for p in sorted((H/'packed').glob('delta-*/*mm')):
 if not (p/'metrology.json').exists():continue
 d=read(p/'measurements.json');a=read(p/'audit.json');m=read(p/'metrology.json');iv=read(p/'invariants.json');sv=read(p/'service.json')
 assert a['all_pairs_enumerated'] and a['all_exact_candidates_completed'] and not a['early_stop']
 cable_ok=all(q['valid'] and q['solids']==1 for q in m['wings'].values())
 gates={
 '1_zero_interference':a['interference_zero'],
 '2_accessible_service':a['interference_zero'] and cable_ok and sv['pass_clearance'] and all(min(w['per_conductor_reserve_mm'])>=30 for w in d['wings']),
 '3_fly_connected_storage':d['fly']['solid_count']==1 and abs(d['fly']['connected_length_mm']-170)<1e-6 and not any('Fly-170mm' in (c['a'],c['b']) for c in a['unexpected_interferences']),
 '4_USB_insertion':d['usb_pass'] and iv['fly_scope_unchanged'],
 '5_retention':a['interference_zero'] and all(q['valid'] and q['solids']==1 for q in d['case_deltas']) and all(q['valid'] and q['solids']==1 and q['within_220x220x250'] for q in m['printing'].values()),
 '6_conductor_200mm':all(max(w['conductor_lengths_mm'])<=200 for w in d['wings'])}
 result=dict(gates=gates,all_gates_pass=all(gates.values()),scope='CAD study acceptance as #244; local retention screens inherited; physical service/load/inversion and harness manufacture remain prototype acceptance')
 for w in d['wings']:
  w['accessible_reserve_certified']=gates['2_accessible_service']
  w['service_evidence']='service.json'
 (p/'measurements.json').write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
 (p/'gates.json').write_text(json.dumps(result,indent=2)+'\n')
 print(p.relative_to(H),result)
