"""Read-only swept harness against all Main top footprints and all 42 keycaps.
Main KiCad -> assembly is (x-100,y-70), not the Wing (x-100,100-y).
Both the Stage1 phi2 screen and a physically plausible <=phi5 bundle are tested.
"""
from pathlib import Path
import csv,json,math,hashlib
import pcbnew as p
from shapely.geometry import Polygon,Point,LineString,box
from shapely.affinity import affine_transform
E=Path(__file__).resolve().parent;R=E.parents[3]
g=json.loads((R/'hardware/case/issue-200-stage1/geometry.json').read_text());main=R/'hardware/kicad/qualification/issue-196-main-rev4-phaseb/inspection/final/main.kicad_pcb';b=p.LoadBoard(str(main))
footprints=[]
for f in b.GetFootprints():
 if f.GetLayer()!=p.F_Cu:continue
 if all(a.GetAttribute()==p.PAD_ATTRIB_NPTH for a in f.Pads()):continue
 r=f.GetBoundingBox(False,False);body=box(r.GetX()/1e6-100,r.GetY()/1e6-70,(r.GetX()+r.GetWidth())/1e6-100,(r.GetY()+r.GetHeight())/1e6-70)
 footprints.append((f.GetReference(),f.GetValue(),body))
results=[];allpairs=[]
for v in g['variants']:
 caps=[]
 for other in g['variants']:
  if other['pitch_mm']!=v['pitch_mm']:continue
  s=json.loads((E/('wing-rev3-'+other['variant'])/'definition.json').read_text());m=other['transform']['matrix'];t=other['transform']['translation']
  for k in s['keys']:
   a=math.radians(k['rotation_ccw_deg']);cx,cy=k['x_mm'],k['y_mm']
   poly=Polygon([(cx+dx*math.cos(a)-dy*math.sin(a),cy+dx*math.sin(a)+dy*math.cos(a)) for dx,dy in [(-8.5,-8.5),(8.5,-8.5),(8.5,8.5),(-8.5,8.5)]])
   caps.append((k['key'],affine_transform(poly,[m[0][0],m[0][1],m[1][0],m[1][1],*t])))
 line=LineString(v['harness']['smooth_samples_assembly']);own=v['harness']['main_ref'];cases=[]
 for diameter in (2.,5.):
  tube=line.buffer(diameter/2,quad_segs=128);under=[];othergaps=[]
  for ref,mpn,body in footprints:
   gap=tube.distance(body);hit=tube.intersects(body)
   allpairs.append(dict(variant=v['variant'],diameter_mm=diameter,reference=ref,value=mpn,footprint_bbox_mm=list(body.bounds),planar_gap_mm=gap,under_sweep=hit,intended_mating=(ref==own)))
   if hit:
    assert ref==own,(v['variant'],diameter,ref,'new overhead obstacle needs height assessment')
    under.append(dict(reference=ref,value=mpn,mated_reference_height_mm=7.3,reserved_mated_height_mm=8.,mated_reference_top_z_mm=18.5,reservation_top_z_mm=19.2,horizontal_cable_center_z_mm=24.2,horizontal_cable_bottom_z_mm=24.2-diameter/2,horizontal_gap_to_reservation_mm=5-diameter/2,endpoint='intentional plug/wire interface; zero separation at attachment, then vertical/R5 rise'))
   if ref!=own:othergaps.append((gap,ref))
  keygap=min(tube.distance(k) for _,k in caps);hits=[name for name,k in caps if tube.intersects(k)];assert not hits
  # UDB outline is the unchanged #198 assembly shape saved by Stage1.
  dims=json.loads((R/f'hardware/case/issue-200-stage1/inputs/issue198/dimensions-{v["pitch_mm"]}mm.json').read_text())
  udb=Polygon(dims['boards']['udb']['outline'])
  udbgap=tube.distance(udb);assert udbgap>0
  cases.append(dict(diameter_mm=diameter,main_components_under_sweep=under,all_other_main_top_footprints_clear=True,other_main_min_planar_gap_mm=min(othergaps)[0],other_main_nearest_reference=min(othergaps)[1],keycap_count=len(caps),keycap_intersections=hits,keycap_gap_mm=keygap,udb_gap_mm=udbgap,cable_top_z_mm=24.2+diameter/2,lid_or_retainer_min_inner_z_mm=24.2+diameter/2+.5))
 # Two vertical-to-horizontal R5 quarter-circles replace 5mm at each endpoint.
 smooth=v['harness']['smooth_length_mm'];bent=smooth+2*(math.pi*5/2-5)
 assert v['harness']['required_mm']>bent
 results.append(dict(variant=v['variant'],waypoints_assembly=v['harness']['waypoints_assembly'],xy_route_change_required=False,planar_route_mm=smooth,proposed_z_bend_radius_mm=5.,centerline_with_two_z_bends_mm=bent,required_conductor_length_mm=v['harness']['required_mm'],remaining_allowance_after_z_bends_mm=v['harness']['required_mm']-bent,gh_access_z_mm=v['connector']['access_z_mm'],cases=cases))
output=dict(main_top_footprints_checked=len(footprints),main_source_sha256=hashlib.sha256(main.read_bytes()).hexdigest(),main_to_assembly='(x-100,y-70)',height_source='JST eGH.pdf pages 2-3: top-entry assembly reference (7.3), not a certified tolerance limit',height_source_url='https://www.jst-mfg.com/product/pdf/eng/eGH.pdf',bundle_rule='14 wires, each insulation OD <=1mm, controlled hexagonal packing within diameter5mm (19-site packing capacity). Sleeve/retainer included in the <=5mm procurement/assembly envelope.',phi2_limitation='phi2 is only Stage1 screening: even 14*OD0.76mm circular wire areas exceed phi2 cross-section. Do not specify phi2 as the completed 14-wire harness.',limitations=['8mm mated-height and phi5/R5 are assembly design reservations; actual harness must meet them','Only native top footprint/pad envelopes are known; fitted bodies must remain within these envelopes','At GH endpoint the plug is an intentional attachment, not an obstacle cleared by an air gap','Lid and retainers must clear cable top by 0.5mm; case changes belong to Issue198','200mm surplus retention in central/north space, strain relief, wire ordering and actual minimum bend radius require physical fit confirmation'],variants=results)
(E/'harness-clearance.json').write_text(json.dumps(output,indent=2)+'\n')
with (E/'harness-main-all-pairs.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(allpairs[0]));writer.writeheader();writer.writerows(allpairs)
print(json.dumps(results,indent=2))
