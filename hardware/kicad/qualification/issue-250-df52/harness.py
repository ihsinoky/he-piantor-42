"""Conservative mated and first-dress STEP envelopes; dimensions in mm.
Not a detailed manufacturer mechanical model. Native KiCad board top datum Z=0.
"""
from pathlib import Path
import json,math,hashlib
from build123d import Solid,Plane,Compound,Vector,export_step,Axis
E=Path(__file__).resolve().parent;W=E/'harness';W.mkdir(exist_ok=True)
# Local frame: x along numbered row, y outward mating/exit, z away from PCB.
body=Solid.make_box(13.4,4.1,1.75).translate(Vector(-6.7,-1.26,0))
wires=[]
for i in range(14):wires.append(Solid.make_cylinder(.3,10,Plane(origin=(-5.2+.8*i,2.84,.875),z_dir=(0,1,0))))
local=Compound(children=[body,*wires]);export_step(local,str(W/'mated-and-first-dress-local.step'))
records=[]
for w in [E/'main',*sorted(E.glob('wing-rev4-*'))]:
 for pose in json.loads((w/'construction.json').read_text())['poses']:
  x,y=pose['native_origin_mm'];a=pose['angle_deg'];bottom=pose['side']=='B.Cu';z=-1.2 if bottom else 0
  shape=local.rotate(Axis.X,180) if bottom else local
  shape=shape.rotate(Axis.Z,-a).translate(Vector(x,y,z));fn=f'{w.name}-{pose["ref"]}.step';export_step(shape,str(W/fn))
  ang=math.radians(a);sgn=-1 if bottom else 1
  matrix=[[math.cos(ang),sgn*math.sin(ang),0,x],[-math.sin(ang),sgn*math.cos(ang),0,y],[0,0,sgn,z],[0,0,0,1]]
  box=shape.bounding_box();records.append(dict(board=w.name,ref=pose['ref'],file=fn,sha256=hashlib.sha256((W/fn).read_bytes()).hexdigest(),local_to_native_board_mm=matrix,native_exit_unit_xy=[sgn*math.sin(ang),sgn*math.cos(ang)],native_bounds_mm=[box.min.X,box.min.Y,box.min.Z,box.max.X,box.max.Y,box.max.Z],assembly_transform='Main B3 native datum: x_assembly=x_native-100, y_assembly=y_native-70; Z requires B3 mounting datum' if not bottom else 'For planar case: local_wing=(x_native-100,100-y_native), then hardware/case/issue-228-final/{pitch}mm/dimensions.json wing_transforms[hand]; mounting-face normal is underside. Apply Phase B Z datum.'))
manifest=dict(units='mm',kind='case keepout solid; not exact manufacturer model',local_frame='x numbered row (cavity1 x=-5.2), +y mate/exit, +z away from mounting face',body_local_bounds_mm=[-6.7,-1.26,0,6.7,2.84,1.75],first_dress='14 individual 0.60 mm OD cylinders, .80 mm pitch; y=2.84..12.84, z=.875; first 10 mm straight and flat; no gathering before rear+10 mm',first_restraint_mm_from_exit=10,wire_gauge='AWG28 UL1571 thin-wall 7/0.127 mm, OD .50-.60 mm',finished_conductor_spec_mm=dict(nominal=195,tolerance=5,maximum=200,service_reserve_included=30.2,maximum_active_path_excluding_reserve=169.8),cavity_mapping='n to n at both ends, six independent grounds 2/4/8/10/12/14; MP is not a cable cavity',wing_underside_B_mm=6.70,main_roof_screen=dict(unchanged_poses=True,B3_nominal_clearance_mm=1.90,allowance_mm=.50,after_allowance_mm=1.40,required_minimum_mm=.30,status='PASS at supplied B3 datum; not a fresh roof solid collision study'),endpoints=records)
(W/'geometry.json').write_text(json.dumps(manifest,indent=2)+'\n');print(len(records),'native endpoint envelopes')
