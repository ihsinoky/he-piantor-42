"""Regenerate #150 case inputs from Rev.3 definitions, in both coordinate frames."""
from pathlib import Path
import csv,json,sys
R=Path(__file__).resolve().parents[3];E=Path(__file__).resolve().parent

def write(name,rows):
 with (E/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for pitch in (16,17):
 for side in ('left','right'):
  s=json.loads((R/f'hardware/kicad/qualification/issue-200-wing-rev3/wing-rev3-{pitch}mm-{side}/definition.json').read_text());name=f'{pitch}mm-{side}';cs={c['reference']:c for c in s['components']}
  write(f'keys-{name}.csv',[dict(key=k['key'],sensor=k['sensor'],x_mm=k['x_mm'],y_mm=k['y_mm'],kicad_x_mm=100+k['x_mm'],kicad_y_mm=100-k['y_mm'],rotation_deg=k['rotation_ccw_deg'],hall_origin_x_mm=cs[k['sensor']]['x_mm'],hall_origin_y_mm=cs[k['sensor']]['y_mm'],hall_side='bottom') for k in s['keys']])
  write(f'holes-{name}.csv',[dict(reference=f'H{i}',kind='mounting',x_mm=h['x_mm'],y_mm=h['y_mm'],diameter_mm=h['diameter_mm'],keepout_diameter_mm=5) for i,h in enumerate(s['mounting_holes'],1)]+[dict(reference=f'MH_{i}_{j}',kind='locator',x_mm=h['x_mm'],y_mm=h['y_mm'],diameter_mm=h['diameter_mm'],keepout_diameter_mm=2.2) for i,k in enumerate(s['keys'],1) for j,h in enumerate(k['locator_holes'],1)])
  write(f'outline-{name}.csv',[dict(vertex=i,x_mm=xy[0],y_mm=xy[1]) for i,xy in enumerate(s['outline_mm'],1)])
