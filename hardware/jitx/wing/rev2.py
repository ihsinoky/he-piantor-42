"""Wing Rev.2 PCB coordinates from the approved Phase A layout."""
import argparse, json, math
from html import escape
from pathlib import Path
from wing.export import artifacts
ROOT=Path(__file__).resolve().parents[3]
ACTIVE_DELTA_MM=(0.0,0.0)
def define_rev2(pitch,side):
 assert pitch in (16,17) and side in ('left','right')
 s=json.loads((ROOT/f'hardware/case/issue-194-layout/definition-{pitch}mm-{side}.proposal.json').read_text())
 # PO 2026-11-07: trim south to switch support, chamfer inner south corner.
 original=[list(v) for v in s['outline_mm']]
 x0,y0=original[0];x1,y1=original[2]
 south=min(y for k in s['keys'] for x,y in k['envelope_mm'])
 cut={16:3.956,17:3.928}[pitch]
 if side=='left':
  s['outline_mm']=[[x0,south],[x1-cut+(south-y0),south],[x1,y0+cut],[x1,y1],[x0,y1]]
 else:
  s['outline_mm']=[[x0,y0+cut],[x0+cut-(south-y0),south],[x1,south],[x1,y1],[x0,y1]]
 # Keep H1/H3 identities; move southern outer hole with edge and inner hole above T2.
 for h in s['mounting_holes']:
  if abs(h['y_mm']-(y0+3))<1e-6:
   inner=(h['x_mm']>0) if side=='left' else (h['x_mm']<0)
   h['y_mm']=(-15 if pitch==16 else -17) if inner else south+3
 s['south_cut']=dict(original_outline_mm=original,inner_corner_cut_mm=cut,south_limit_mm=south,kind='45 degree inner chamfer plus south support trim',mounting_holes='outer south follows new edge; inner south moved north 15.8mm for T2 keepout')
 s['width_mm']=max(x for x,y in s['outline_mm'])-min(x for x,y in s['outline_mm'])
 s['height_mm']=max(y for x,y in s['outline_mm'])-min(y for x,y in s['outline_mm'])
 s['outline_policy']='PO 2026-11-07: south edge at full switch envelope limit; 45 degree south inner chamfer; four mounting centers >=3mm from boundary and phi5 circles >=0.25mm from switches'
 s.update(name=f'wing-rev2-{pitch}mm-{side}',schema_version='wing-rev2-1',status='Phase B PCB definition; qualification in issue-194-wing-rev2',size_requirement='Phase A plus PO south inner chamfer 2026-11-07')
 for c in s['components']:
  if c['kind']=='hall':
   a=math.radians(c['rotation_ccw_deg']);dx,dy=ACTIVE_DELTA_MM
   c['active_target_mm']=[c['x_mm'],c['y_mm']]
   c['x_mm']-=math.cos(a)*dx-math.sin(a)*dy;c['y_mm']-=math.sin(a)*dx+math.cos(a)*dy
 s['hall_pose_contract'].update(target_active_xy='F=K-R(theta)delta; delta=(0,0) mm nominal; TI Rev.C Fig6-5 centered +/-0.05mm',locator_status='Nominal manufacturing design adopts +/-5.08, diameter1.70; finished diameter tolerance +/-0.05 required; physical fit remains unmeasured',active_delta_mm=list(ACTIVE_DELTA_MM),bottom_transform='native flip then set top-view CCW angle; bottom local (x,y) maps to (x,-y) at zero angle; same transform on both boards')
 s['routing_rules']=dict(signal_width_mm=.1,power_ground_width_mm=.3,clearance_mm=.1,via_diameter_mm=.6,via_drill_mm=.3,via_pad_design_target_mm=.15)
 return s
def placement_svg(s):
 x0=min(x for x,y in s['outline_mm']);x1=max(x for x,y in s['outline_mm']);y0=min(y for x,y in s['outline_mm']);y1=max(y for x,y in s['outline_mm'])
 lines=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0-3} {-y1-7} {x1-x0+6} {y1-y0+13}" width="1200" height="{1200*(y1-y0+13)/(x1-x0+6)}">','<polygon points="'+' '.join(f'{x},{-y}' for x,y in s['outline_mm'])+'" fill="#f8faf9" stroke="#333" stroke-width=".12"/>',f'<text x="{x0}" y="{-y1-3}" font-size="2">{s["name"]}: placement definition; top view</text>']
 for k in s['keys']:
  points=' '.join(f'{x},{-y}' for x,y in k['envelope_mm']);lines.append(f'<polygon points="{points}" fill="none" stroke="#acb8bc" stroke-width=".08"/>')
  for h in k['locator_holes']:lines.append(f'<circle cx="{h["x_mm"]}" cy="{-h["y_mm"]}" r=".85" fill="white" stroke="#444" stroke-width=".08"/>')
 for h in s['mounting_holes']:
  for radius in (2.5,1.1):lines.append(f'<circle cx="{h["x_mm"]}" cy="{-h["y_mm"]}" r="{radius}" fill="none" stroke="#555" stroke-width=".08"/>')
 for c in s['components']:
  color='#a64c4c' if c['side']=='bottom' else '#40697c';lines.append(f'<circle cx="{c["x_mm"]}" cy="{-c["y_mm"]}" r=".6" fill="{color}"><title>{escape(c["reference"]+" "+c["side"])}</title></circle>')
 lines.append('</svg>');return '\n'.join(lines)+'\n'
def export(check=False):
 for pitch in (16,17):
  for side in ('left','right'):
   s=define_rev2(pitch,side)
   data=artifacts(s);data['placement.svg']=placement_svg(s)
   for name,content in data.items():
    p=ROOT/'hardware/jitx/wing/generated'/s['name']/name
    if check:assert p.read_text()==content,p
    else:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');export(p.parse_args().check)
