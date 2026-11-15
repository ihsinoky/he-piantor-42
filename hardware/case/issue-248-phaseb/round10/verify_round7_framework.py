"""Round-7 strand-only scope and evidence binding; no CAD dependencies."""
import json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify_paths():
 pm=read(H/'pinmap-round7.json');old=read(H/'round5/pinmap-round5.json');proto=read(H/'routes-round7-prototype.json');cert=read(H/'curve-certificates-round7.json')
 assert pm['passed'] and len(pm['wires'])==28 and pm['routes_sha256']==sha(H/'routes-round7-prototype.json')
 for a,b in zip(pm['wires'],old['wires']):
  for k in ('side','wire','wing_pin','main_pin','wing_endpoint_mm','main_endpoint_mm'):assert a[k]==b[k],(a['side'],a['wire'],k)
 assert cert['passed'] and cert['prototype_sha256']==sha(H/'routes-round7-prototype.json')
 for w,p in zip(proto['right'],cert['strands']):
  assert w['pin']==p['pin'] and p['passed'] and p['minimum_radius_lower_bound_mm']>=5
  assert abs(p['length_delta_mm'])<1e-6 and w['finished_length_mm']<=200
 assert proto['reserve_mm']==30.2 and proto['service_translation_mm']==15.1
 for rd in (3,4,5):
  manifest=read(H/f'round{rd}-sha256.json')['files']
  for n,digest in manifest.items():assert sha(H/f'round{rd}'/n)==digest,('frozen evidence changed',rd,n)
 for n,digest in read(H/'round6-sha256.json').items():assert sha(H/'round6'/n)==digest,('frozen round6 changed',n)
 return True

def verify_fixed(pitch):
 out=H/f'{pitch}mm';old=read(H/f'round5/{pitch}mm/assembly-index.json');idx=read(out/'assembly-index.json');proof=read(out/'round7-fixed-scope.json')
 assert proof['geometry_sha256']==sha(out/'assembly-index.json') and proof['baseline_index_sha256']==sha(H/f'round5/{pitch}mm/assembly-index.json')
 assert proof['all_fixed_byte_identical'] and len(old)==len(idx)
 changed=[]
 for a,b in zip(old,idx):
  assert a['name']==b['name'] and a['solid']==b['solid']
  if not a['name'].startswith('Wire-'):assert a==b,('unauthorized fixed change',pitch,a['name'])
  elif a!=b:changed.append(a['name'])
 assert proof['changed_names']==changed and len(changed)==28
 meta=read(out/'measurements.json');baseline=read(H/f'round5/{pitch}mm/measurements.json')
 for k,v in baseline.items():
  if k not in ('wings','wire_sweep_checks'):assert meta[k]==v,('fixed metadata changed',pitch,k)
 for w in meta['wings']:
  assert w['service_turn_y_mm']==[17.1,2.0]
  assert len(w['conductor_lengths_mm'])==14 and all(abs(v-30.2)<1e-6 for v in w['per_wire_reserve_mm'])
  assert max(w['conductor_lengths_mm'])+7.3<=200
  for r in w['analytic_segments']:
   assert r['round7_curve_certificate']['passed'] and r['round7_curve_certificate']['minimum_radius_lower_bound_mm']>=5
   assert r['return_initial_straight_lower_bound_mm']>15.7
 return True

def verify_comparisons(pitch):
 from collections import Counter
 out=H/f'{pitch}mm';comparison=read(out/'round7-comparison.json');current=read(out/'audit.json')
 assert comparison['geometry_sha256']==sha(out/'assembly-index.json')
 def category(n):
  for prefix,label in [('Wire-','conductors'),('plate-screw-','E screws'),('plate-','aluminium plates'),('tray-','trays'),('underside-','Wing underside bounds')]:
   if n.startswith(prefix):return label
  return n
 def counts(a):return Counter(' / '.join(sorted([category(r['a']),category(r['b'])])) for r in a['unexpected_interferences'])
 def pairs(a):return {tuple(sorted((r['a'],r['b']))) for r in a['unexpected_interferences']}
 assert {r['round'] for r in comparison['baselines']}=={3,4,5,6}
 for row in comparison['baselines']:
  path=H/f"round{row['round']}/{pitch}mm/audit.json";base=read(path);aa=counts(base);bb=counts(current)
  assert row['baseline_audit_sha256']==sha(path)
  assert row['categories']=={n:dict(baseline=aa[n],round7=bb[n]) for n in sorted(set(aa)|set(bb))}
  assert row['cleared_named_pairs']==[list(p) for p in sorted(pairs(base)-pairs(current))]
  assert row['remaining_named_pairs']==[list(p) for p in sorted(pairs(base)&pairs(current))]
  assert row['new_named_pairs']==[list(p) for p in sorted(pairs(current)-pairs(base))]
 return True
if __name__=='__main__':
 verify_paths()
 for pitch in (17,16):verify_fixed(pitch);verify_comparisons(pitch)
 print('Round7: frozen round5 fixed scope, continuous curve bounds, native maps and comparisons PASS')
