"""Check evidence consistency. A rejected routing must remain rejected."""
import json,hashlib
from pathlib import Path
E=Path(__file__).resolve().parent;R=E.parents[2]
snap=json.loads((R/'hardware/kicad/qualification/issue-240-main-rev7/inspection/final/snapshot.json').read_text());fs={c['ref']:c for c in snap['components']}
for pitch in [16,17]:
 d=json.loads((E/f'{pitch}mm/measurements.json').read_text())
 assert d['unexpected_interferences']==len(d['collisions'])>0
 assert d['verdict'].startswith('INFEASIBLE')
 assert abs(d['fly']['connected_length_mm']-170)<1e-7 and d['fly']['solid_count']==1
 assert abs(d['fly']['volume_mm3']-170*3.141592653589793)<.001
 assert len(d['wings'])==2 and all(abs(w['longest_connected_conductor_mm']-160)<1e-7 for w in d['wings'])
 assert d['cover_top_z_mm']==16.2 and all(0<r['remaining_skin_mm']<1.5 for r in d['cover_reliefs'])
 for r,ref in zip(d['gh_placement'],['J2','J3']):
  c=fs[ref];assert abs(c['angle']-r['orientation_deg'])<1e-8
  assert max(abs(c['position'][i]-[100,70][i]-r['origin_mm'][i]) for i in [0,1])<=.000002
 assert d['usb_pass']
 for name in ['cover-trial.step','fly-170mm.step','wing-left-160mm.step','wing-right-160mm.step','assembly-with-cover-REJECTED.step']:assert (E/f'{pitch}mm'/name).stat().st_size>1000
for p,h in json.loads((E/'inputs-sha256.json').read_text()).items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
print('Study evidence consistency PASS; full assembly physical acceptance FAIL as reported')
