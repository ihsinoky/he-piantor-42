"""Dependency-free enforcement of assignment-only path and frozen solid scope."""
import json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify_paths():
 old=read(H/'round3/routes-round3.json');new=read(H/'routes-round6.json')
 for k in ('centre_x_mm','turn_centre_y_mm','service_travel_mm'):assert old[k]==new[k]
 assert new['centre_x_mm']==17.4 and new['turn_centre_y_mm']==10 and new['service_travel_mm']==15.1
 for i in range(14):
  assert new['before'][i]==old['before'][13-i]
  assert new['after'][i][:-2]==old['after'][13-i][:-2]
  assert new['after'][i][-2:]==old['after'][i][-2:]
 # Bound generated data to immutable native-verified physical map.
 newmap=read(H/'pinmap-round6.json');oldmap=read(H/'pinmap-round4.json')
 assert newmap['routes_sha256']==sha(H/'routes-round6.json')
 for a,b in zip(newmap['wires'],oldmap['wires']):
  for key in ('side','wire','wing_pin','main_pin','wing_endpoint_mm','main_endpoint_mm'):assert a[key]==b[key]
 return True

def verify_fixed(pitch):
 out=H/f'{pitch}mm';proof=read(out/'frozen-framework-recovery.json');old=read(H/f'round3/{pitch}mm/assembly-index.json');idx=read(out/'assembly-index.json')
 assert proof['baseline_index_sha256']==sha(H/f'round3/{pitch}mm/assembly-index.json')
 assert len(old)==len(idx)
 recovery={r['part']:r for r in proof['recovery']}
 frozen=read(H/'round3-sha256.json')['files']
 for a,b in zip(old,idx):
  n=a['name'];assert a['name']==b['name'] and a['solid']==b['solid']
  if n.startswith('Wire-'):continue
  r=recovery[n]
  if r['method']=='byte-identical frozen BRep':
   assert r['sha256']==a['sha256']
   if n!='tray-left':assert a==b,('unapproved fixed change',n)
  else:
   assert n in ('tray-left','tray-right','shell-central')
   source=H/r['source_file'];assert r['source_sha256']==sha(source)==frozen[str(source.relative_to(H/'round3'))]
   assert a['sha256']==r['frozen_brep_sha256']
   if n!='tray-left':assert b['sha256']==r['recovered_brep_sha256'],('unapproved STEP-recovered change',n)
   assert abs(r['volume_delta_mm3'])<.001 and r['maximum_bounds_delta_mm']<1e-5
  if n=='tray-left':
   repair=read(out/'splice-boss-rebuild.json')
   assert repair['geometry_sha256']==sha(out/'assembly-index.json')
   assert abs(a['volume_mm3']+r.get('volume_delta_mm3',0)-repair['before_volume_mm3'])<1e-6
   assert abs(b['volume_mm3']-repair['after_volume_mm3'])<1e-6
 meta=read(out/'measurements.json');base_meta=read(H/f'round3/{pitch}mm/measurements.json');design=read(H/'routes-round6.json')
 assert meta['route_channel_reservation']==base_meta['route_channel_reservation']
 for w in meta['wings']:
  sign=-1 if w['side']=='left' else 1
  assert w['service_turn_y_mm']==[10,-5.1] or all(abs(a-b)<1e-10 for a,b in zip(w['service_turn_y_mm'],[10,-5.1]))
  for i,row in enumerate(w['analytic_segments']):
   j=13-i if sign<0 else i
   before=[[sign*x,y,z] for x,y,z in design['before'][j]];after=[[sign*x,y,z] for x,y,z in design['after'][j]]
   assert row['before']==before and row['after']==after
   assert abs(row['turn_radius_mm']-(17.4-design['before'][j][-1][0]))<1e-10
   released=w['released_analytic_segments'][i]
   before[-1][1]=after[0][1]=10-15.1
   assert released['before']==before and released['after']==after
   assert abs(w['per_wire_reserve_mm'][i]-30.2)<1e-6

 return True
if __name__=='__main__':
 verify_paths()
 for pitch in (17,16):verify_fixed(pitch)
 print('Frozen round-3 final framework and assignment-only deviations PASS')
