"""Export top-view native pad and package-body assembly reference, vector SVG/PDF."""
from common import *
import html
spec=json.loads((SOURCE/'definition.json').read_text());inv=json.loads((E/'manufacturing/native-inventory.json').read_text());review=json.loads((E/'assembly-review.json').read_text());parts={p['reference']:p for p in review['parts']}
lines=['<svg xmlns="http://www.w3.org/2000/svg" width="1536" height="1152" viewBox="28 48 144 108">','<rect x="28" y="48" width="144" height="108" fill="white"/>','<style>text{font-family:monospace;font-size:.9px} .pad{fill:#d7a34d;stroke:#926f28;stroke-width:.04} .body{fill:#b8dded;fill-opacity:.6;stroke:#26708a;stroke-width:.15}</style>','<text x="36" y="51" style="font-size:1.5px">M1 MATRIX18 — TOP ASSEMBLY / 16mm + 17mm</text>','<text x="36" y="54">Native copper pads + package bodies; red dot = pad 1; blue cross = CPL body centroid.</text>','<text x="36" y="56">Review orientation against pad numbers; no bottom parts; units mm; not a switch mounting drawing.</text>','<rect x="36" y="60" width="128" height="80" fill="none" stroke="#333" stroke-width=".2"/>']
for s in spec['sensor_sites']:
 x,y=100+s['x_mm'],100-s['y_mm'];h=s['block_pitch_mm']/2
 lines.append(f'<rect x="{x-h}" y="{y-h}" width="{2*h}" height="{2*h}" fill="none" stroke="#bbb" stroke-width=".1"/>')
for c in spec['components']:
 if c['kind']=='testpoint':continue
 ref=c['reference'];r=parts[ref];cx,cy=r['body_centroid_kicad_mm'];w,h={'hall':(1.3,2.92),'mux':(4.4,5),'capacitor':(1.6,.8),'connector':(20.75,4.25)}[c['kind']]
 lines.append(f'<rect class="body" x="{cx-w/2}" y="{cy-h/2}" width="{w}" height="{h}"/>')
 lines.append(f'<path d="M{cx-.35} {cy}h.7 M{cx} {cy-.35}v.7" stroke="#047eb3" stroke-width=".12"/>')
 lines.append(f'<text x="{cx}" y="{cy-h/2-1}" text-anchor="middle">{html.escape(ref)}</text>')
for q in inv['pads']:
 x,y=q['pos'];w,h=q['size'];a=q['angle_deg'];color='#b1b1b1' if q['ref'].startswith('TP_') else '#d7a34d'
 if any(q['drill']):
  lines.append(f'<circle cx="{x}" cy="{y}" r="1.1" fill="white" stroke="#333" stroke-width=".15"/>');continue
 if q['shape']==0:lines.append(f'<circle cx="{x}" cy="{y}" r="{w/2}" fill="{color}"/>')
 else:lines.append(f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" class="pad" transform="rotate({-a} {x} {y})"/>')
 if q['ref'] in parts:
  lines.append(f'<text x="{x}" y="{y+.18}" style="font-size:.48px" text-anchor="middle">{html.escape(q["number"])}</text>')
  if q['number']=='1':lines.append(f'<circle cx="{x}" cy="{y}" r=".10" fill="#d00"/>')
lines+=['<text x="36" y="145">CPL origin: lower-left board edge (KiCad 36,140), X right / Y up. All top rotations 0deg CCW.</text>','<text x="36" y="147">GH14: row origin (100,133), body centroid (100,135.325); CPL (64,4.675)mm. Pin1 remains rightmost.</text>','<text x="36" y="149">ALL 146 plated vias: epoxy fill + copper cap + plate over. Read FABRICATION.md before any release.</text>','</svg>']
d=E/'manufacturing';svg=d/'assembly-top.svg';svg.write_text('\n'.join(lines)+'\n')
import cairosvg
cairosvg.svg2pdf(url=str(svg),write_to=str(d/'assembly-top.pdf'))
cairosvg.svg2png(url=str(svg),write_to=str(d/'assembly-top.png'),output_width=1800,background_color='white')
print('Assembly SVG/PDF/PNG generated')
