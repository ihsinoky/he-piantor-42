"""Classify nominal hardware thread mating; retain every measured raw contact."""
import json,sys
from pathlib import Path
E=Path(__file__).resolve().parent
for pitch in [16,17]:
 p=E/f'{pitch}mm/measurements.json'
 if not p.exists():continue
 d=json.loads(p.read_text());raw=E/f'{pitch}mm/raw-measurements.json'
 if not raw.exists():raw.write_text(p.read_text())
 expected=d.get('nominal_thread_contacts',[]);bad=[]
 for r in d['collisions']:
  a,b=r['a'],r['b']
  thread=(a.startswith('cover-screw-') and b.startswith('cover-nut-') or b.startswith('cover-screw-') and a.startswith('cover-nut-')) and a.split('-')[-1]==b.split('-')[-1]
  if thread and r['overlap_mm3']<.01:expected.append(dict(**r,classification='Nominal thread mating; polygonal nut bore versus analytic shaft envelope'))
  else:bad.append(r)
 d['nominal_thread_contacts']=expected;d['collisions']=bad;d['unexpected_interferences']=len(bad)
 p.write_text(json.dumps(d,indent=2)+'\n')
