"""Independent XY/height underside service-body screen, plus connector tolerances."""
from pathlib import Path
import json,math
from shapely.geometry import box,Polygon
from shapely.affinity import rotate,translate,affine_transform
E=Path(__file__).resolve().parent;rows=[]
for w in sorted(E.glob('wing-rev4-*')):
 d=json.loads((w/'definition.json').read_text());side=w.name.split('-')[-1];sgn=-1 if side=='left' else 1;dims=json.loads((E.parents[3]/f'hardware/case/issue-228-final/{int(d["pitch_mm"])}mm/dimensions.json').read_text());tr=dims['wing_transforms'][side];m=tr['matrix'];t=tr['translation'];af=[m[0][0],m[0][1],m[1][0],m[1][1],*t];bodies=[]
 for c in d['components']:
  if c['kind']=='testpoint':continue
  if c['reference']=='J_WING':g=box(sgn*27-10.875,-43.1,sgn*27+10.875,-34.95);h=4.85
  else:
   width,height,h=(3.4,3.4,3.4) if c['kind']=='hall' else (5.1,6.6,1.4) if c['kind']=='mux' else (2.4,1.6,1.)
   g=affine_transform(translate(rotate(box(-width/2,-height/2,width/2,height/2),c['rotation_ccw_deg']),c['x_mm'],c['y_mm']),af)
  bodies.append((c['reference'],g,h))
 hits=[];service=[]
 for i,(ref,g,h) in enumerate(bodies):
  for other,og,oh in bodies[:i]:
   if ref.startswith(('U_MUX','C_MUX','J_WING')) or other.startswith(('U_MUX','C_MUX','J_WING')):
    gap=g.distance(og);service.append({'a':ref,'b':other,'xy_gap_mm':gap})
    if g.intersection(og).area>1e-8:hits.append({'a':ref,'b':other,'overlap_mm2':g.intersection(og).area})
 rows.append({'variant':w.name,'service_body_overlaps':hits,'nearest_service_pairs':sorted(service,key=lambda a:a['xy_gap_mm'])[:12],'mated_header_nominal_height_mm':4.35,'allowance_mm':.5,'mated_header_reserved_floor_gap_mm':10-2-4.35-.5,'wire_exit_axis_z_mm':8.4,'axis_uncertainty_mm':.5,'maximum_wire_od_mm':1.,'worst_wire_to_board_gap_at_exit_mm':10-(8.4+.5+.5),'cable_floor_gap_nominal_mm':.5,'gathered_bundle_od_max_mm':5.,'tolerance_status':'header .5 mm allowance included; channel .5 nominal floor gap requires installed channel/OD control, not tolerance-certified','pass_body_overlap_screen':not hits})
(E/'body-clearance.json').write_text(json.dumps(rows,indent=2)+'\n');print([(r['variant'],r['service_body_overlaps']) for r in rows])
