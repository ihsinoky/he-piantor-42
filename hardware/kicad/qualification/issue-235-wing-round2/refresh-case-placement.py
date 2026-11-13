"""Rescreen native pads after connector-pose correction; case solids are unchanged.
Native probe check binds the real opening to the already modeled southward exit.
"""
from pathlib import Path
import json,hashlib
from shapely.geometry import Point,shape
from shapely.ops import unary_union
E=Path(__file__).resolve().parent;ROOT=E.parents[3];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
poses=json.loads((E/'connector/placement.json').read_text());assert len(poses)==4 and all(r['native_transformed_probes_pass'] for r in poses)
rows=[]
for pitch in (16,17):
 out=E/f'case/{pitch}mm';posts=json.loads((out/'post-rescreen.json').read_text())
 for row in posts:
  w=E/('wing-rev4-'+row['variant']);union=unary_union([shape(p['geometry']) for p in json.loads((w/'pad-obstacles.json').read_text())]);gap=Point(*row['xy_mm']).buffer(1.5).distance(union)
  row['pad_drill_edge_gap_mm']=gap;row['must_move_for_this_trial']=bool(row['body_hits'] or row['trial_channel_collar_hits'] or gap<.4)
  assert not row['must_move_for_this_trial']
 (out/'post-rescreen.json').write_text(json.dumps(posts,indent=2)+'\n');rows.extend(posts)
manifest=json.loads((E/'case/inputs-sha256.json').read_text())
changed=[]
for name,expected in list(manifest.items()):
 p=ROOT/name;now=sha(p)
 if now==expected:continue
 assert p.parent.parent==E and p.name in ('definition.json','pad-obstacles.json'),('unexpected case input change',name)
 changed.append(name);manifest[name]=now
(E/'case/inputs-sha256.json').write_text(json.dumps(manifest,indent=2)+'\n')
(E/'case/placement-refresh.json').write_text(json.dumps({'native_exit_probes_pass':True,'case_geometry_changed':False,'modeled_real_exit_xy_matches_native':True,'refreshed_native_pad_input_hashes':changed,'rescreened_posts':len(rows),'post_moves':0,'note':'Corrected PCB header orientation now matches the previously modeled southward connector opening. Body, fanout, channel and proposal STEP geometry are unchanged.'},indent=2)+'\n')
print('Native-pose bound case placement refreshed; all',len(rows),'posts remain legal')
