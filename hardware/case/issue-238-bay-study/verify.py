"""Read-only study consistency checks. A passing verifier confirms an INFEASIBLE result."""
import json,hashlib,math
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2]
for n,h in json.loads((P/'inputs-sha256.json').read_text()).items():
 assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
inv=json.loads((P/'main-inventory.json').read_text())
assert len(inv)==59 and sum(r['ref'].startswith('TP') for r in inv)==4
assert all(r['side']=='F.Cu' for r in inv)
assert abs(11.2+7.3-16.2-2.3)<1e-10
for pitch in (16,17):
 d=json.loads((P/f'{pitch}mm-measurements.json').read_text())
 assert d['verdict']=='INFEASIBLE' and d['probe_interferences']
 assert any(x['part']=='Main-study-J2' for x in d['probe_interferences'])
 assert any(x['part']=='Main-study-J3' for x in d['probe_interferences'])
 assert all(x['cover_swept_bbox_overlap_mm3']<1e-7 for x in d['usb_probe'])
 f=d['fly_trial'];assert abs(f['connected_length_mm']-170)<1e-7
 assert abs(f['volume_mm3']-170*math.pi)<1e-4
 assert f['minimum_bend_radius_mm']==5 and f['top_z_mm']<14.7
 assert f['passed']==(not bool(f['obstacles_with_gap_below_point3_mm']))
 for v in d['volumes'].values():
  assert 0<v['free_mm3']<v['gross_mm3']
  assert abs(sum(x['intersection_mm3'] for x in v['subtractions'])-v['removed_mm3'])<1e-4
for n in ('top-view.svg','section-gh.svg','section-bay.svg'):
 import xml.etree.ElementTree as ET
 ET.parse(P/n)
print('PASS: inputs unchanged; dimensions, connected length/volume, negative-fit evidence, USB-cover sweep and SVG syntax consistent.')
print('Design verdict remains INFEASIBLE; no full-assembly zero-interference pass is claimed.')
