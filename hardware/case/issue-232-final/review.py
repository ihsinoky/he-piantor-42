"""Dimensioned top/cutaway SVGs from generated outlines and stored cable waypoints."""
from geometry import *

def path(g):
 out=[]
 for p in polygons(g):
  for r in [p.exterior,*p.interiors]:out.append('M'+' L'.join(f'{x:.4f},{y:.4f}' for x,y in r.coords)+' Z')
 return ' '.join(out)

def run(pitch):
 out=HERE/f'{pitch}mm';d=json.loads((out/'dimensions.json').read_text());od=json.loads((BASE/f'{pitch}mm/outline-check.json').read_text());outer=Polygon(od['outer_xy_mm'])
 x0,y0,x1,y1=outer.bounds
 lines=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="1000" viewBox="{x0-8} {y0-22} {x1-x0+16} {y1-y0+50}">','<rect x="-300" y="-200" width="600" height="500" fill="#faf9f5"/>',f'<text x="{x0}" y="{y0-12}" font-family="sans-serif" font-size="5">Issue 232 · {pitch} mm · full-cover Wing decks + dressed 160 mm harness</text>',f'<path d="{path(outer)}" fill="#aaa69d" stroke="#383e42" stroke-width=".35"/>']
 for side in ('left','right'):
  pl=shape(json.loads((out/f'plate-package/plate-{side}.geojson').read_text()))
  lines.append(f'<path d="{path(pl)}" fill="#bfcbd0" fill-rule="evenodd" stroke="#394b55" stroke-width=".15"/>')
 for p in d['posts']:
  x,y=p['xy_mm'];lines.append(f'<circle cx="{x}" cy="{y}" r="2.25" fill="#df9c45" opacity=".8"/><text x="{x+2.5}" y="{y}" font-family="sans-serif" font-size="2.7">{p["id"]}</text>')
 for route in d['routes']:
  pts=route['waypoints_mm'];lines.append('<polyline points="'+' '.join(f'{x},{y}' for x,y,z in pts)+'" fill="none" stroke="#21748e" stroke-width="1.1" stroke-dasharray="2 1"/>')
 fly=d.get('fly_dressing')
 if fly:
  pts=fly['waypoints_mm'];lines.append('<polyline points="'+' '.join(f'{x},{y}' for x,y,z in pts)+'" fill="none" stroke="#af5a57" stroke-width=".6" stroke-dasharray="1 1"/>')
 for h in d['mounts']:
  x,y=h['xy'];lines.append(f'<circle cx="{x}" cy="{y}" r="1.7" fill="#46535a"/>')
 lines.extend([f'<text x="{x0}" y="{y1+10}" font-family="sans-serif" font-size="3.5">Blue: Wing route control polygons (STEP bends R5). Red: 170 mm Fly, stored at Z32.5.</text>',f'<text x="{x0}" y="{y1+16}" font-family="sans-serif" font-size="3.5">Orange: six removable supports / Wing below deck. South shelves: fully backed, no new screws.</text>',f'<text x="{x0}" y="{y1+22}" font-family="sans-serif" font-size="3.5">All plate + rim tops Z16.20. Nominal seam 0.20. Central Main / Fly bay remains open.</text>','</svg>'])
 (out/'review-top.svg').write_text('\n'.join(lines))
 lines=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="560" viewBox="0 0 120 56">','<rect width="120" height="56" fill="#faf9f5"/>','<g font-family="sans-serif" font-size="2.4" fill="#263a44">','<text x="3" y="4">E-R section · mm · schematic horizontal scale · exact Z datums</text>', '<rect x="6" y="44" width="100" height="2" fill="#aaa69d"/>','<rect x="6" y="31.3" width="16" height="12.7" fill="#aaa69d"/>','<rect x="6" y="29.8" width="1" height="1.5" fill="#aaa69d"/>','<rect x="7.2" y="29.8" width="96" height="1.5" fill="#bfcbd0"/>','<rect x="24" y="34.8" width="72" height="1.2" fill="#77a177"/>','<rect x="52" y="36" width="3" height="7.5" fill="#df9c45"/>','<rect x="51.25" y="43.5" width="4.5" height=".5" fill="#df9c45"/>','<rect x="52" y="44" width="3.1" height=".8" fill="#df9c45"/>','<rect x="75" y="31.3" width="3.8" height="3.5" fill="#c7c4ab"/>','<rect x="33" y="27" width="14" height="7.8" fill="#526a7a"/>','<rect x="31" y="29.8" width="18" height="1.5" fill="#bfcbd0"/>','<path d="M31,29.4 V23 H49 V29.4" stroke="#b16857" fill="none" stroke-width=".4"/>','<text x="3" y="51">Floor Z0–2 · PCB Z10–11.2 · POM spacer 3.5 · ledge Z14.70 · plate + rim top Z16.20</text>','<text x="3" y="54">Cap outline is the REQUIRED skirt gauge Z≥16.60; an actual purchased cap profile remains unverified.</text>','<text x="9" y="27">No screws in palm shelf</text>','<text x="58" y="40">Post top Z10: nominal gap 0</text>','<text x="80" y="25">Plate 1.50</text>','</g></svg>']
 (out/'review-section.svg').write_text('\n'.join(lines))
if __name__=='__main__':
 for pitch in (16,17):run(pitch)
