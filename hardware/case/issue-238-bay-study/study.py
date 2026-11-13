"""Read-only baseline metrology; numerical slabs and routing probes, not production CAD.
Run reproduce.sh. All output confined to this study and .issue238-runtime.
"""
import sys, csv, json, math, hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.dont_write_bytecode=True
sys.path.insert(0,str(HERE.parent/'issue-232-final'))
from geometry import (leaves,volume,prism,rounded,tube,import_step,Polygon,box,Point,unary_union,shape,mapping,save,coords)
import sexpdata
OUT=HERE
BASE=HERE.parent/'issue-232-final'
D037=HERE.parent/'issue-228-final'
NATIVE=ROOT/'hardware/kicad/qualification/issue-226-main-rev6'
REV4=ROOT/'hardware/kicad/qualification/issue-235-wing-round2'

def bounds(s):
 b=s.bounding_box();return dict(min=[getattr(b.min,k) for k in 'XYZ'],max=[getattr(b.max,k) for k in 'XYZ'])
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ch(n,k):return [x for x in n if isinstance(x,list) and str(x[0])==k]

def inventory():
 board=sexpdata.loads((NATIVE/'inspection/final/main.kicad_pcb').read_text())
 bom={r['ref']:r for r in csv.DictReader((NATIVE/'main-bom.csv').open())}
 native={}
 for f in ch(board,'footprint'):
  props={str(x[1]):str(x[2]) for x in ch(f,'property')}; ref=props['Reference']
  at=ch(f,'at')[0][1:];native[ref]=dict(at_mm=[float(at[0])-100,float(at[1])-70],rotation_deg=float(at[2]) if len(at)>2 else 0,side=str(ch(f,'layer')[0][1]))
 data=[]
 for r in sorted(bom):
  p=bom[r]['part_number']; source=''; h=None
  if r.startswith('TP'):h=0;source='bare copper test pad, native PCB / BOM'
  elif r in ('J2','J3'):h=7.3;source='JST-eGH.pdf p2 assembly layout (reference mated height); vertical exit'
  elif r=='J4':h=1.9;source='D-037 fly.py: Molex 78171/78172 mated stack; official header alone 1.45'
  elif r=='L1':h=2.1;source='Coilcraft XFL4020 mechanical drawing, max'
  elif r=='U1':h=.9;source='RP2040.pdf p608 (printed607), Figure166 A max'
  elif r=='U3':h=.6;source='Winbond.pdf RevJ UX USON2x3 max; ordering table and package drawing'
  elif r=='U4':h=1.3;source='AP2112.pdf p14 SOT25 K max'
  elif r=='U5':h=1.1;source='TPS22919.pdf DCK0006A max'
  elif r=='U6':h=1.;source='TPS63070.pdf RNM0015A max'
  elif r=='Y1':h=.8;source='ABM8-272-T3.pdf drawing456603 RevB mechanical max'
  elif r.startswith('R'):h=.55;source='TNPW.pdf dimension0603 H=0.45+0.10' if r in ('R17','R18') else 'Uniroyal catalog general0603 H=0.45+0.10'
  elif p.startswith('CL05B'):h=.55;source='Samsung CL05B104KO5NNN T=0.50+0.05'
  elif p.startswith('CL05A'):h=.6;source='Samsung CL05A105KA5NQN T=0.50+0.10'
  elif p.startswith('CL10A'):h=.9;source='Samsung CL10A105KB8NNN T=0.80+0.10'
  elif p.startswith('CL21A'):h=1.45;source='Samsung CL21A106KAYNNN T=1.25+0.20'
  elif p.startswith('GRM21'):h=1.45;source='Murata-GRM21.pdf p2 T=1.25+0.20'
  elif p.startswith('C3225'):h=2.8;source='TDK product C3225X7R1C226K250AC T=2.50+0.30'
  elif p.startswith('0402'):h=.55;source='Fenghua exact MPN page T=0.50+0.05'
  assert h is not None,(r,p)
  # Mounting allowance explicit, never represented as a manufacturer's dimension.
  allowance=0 if r.startswith('TP') else .2
  data.append(dict(ref=r,mpn=p,package_height_max_or_reference_mm=h,mounting_allowance_mm=allowance,study_height_mm=h+allowance,study_top_z_mm=11.2+h+allowance,clearance_to_lid_bottom_mm=14.7-11.2-h-allowance,source=source,**native[r]))
 assert len(data)==59 and all(r['side']=='F.Cu' for r in data)
 save(OUT/'main-inventory.json',data)
 with (OUT/'main-inventory.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
 return {r['ref']:r for r in data}

def trial_fly(d):
 from build123d import Edge,Wire,Vector,Plane,Face,sweep
 cy=d['fly']['transform']['translation_mm'][1];start=d['fly']['cable']['waypoints_mm'][0];end=d['fly']['cable']['waypoints_mm'][-1]
 def prefix(south):return [start,[0,cy+10,8.6],[-9,cy+17,5],[-9,south,5],[9,south,5],[9,-18,5],[9,-30,12.6],[-4,-30,12.6],[-4,-12,12.6]]
 # Exact two-arc S shifts, R5 throughout, vertical tangents at both ends.
 def shift(x,y,dx):
  sign=1 if dx>0 else -1;t=math.acos(1-abs(dx)/10);dy=10*math.sin(t)
  p0=Vector(x,y,12.6);pm=Vector(x+dx/2,y+dy/2,12.6);pe=Vector(x+dx,y+dy,12.6)
  m1=Vector(x+sign*5*(1-math.cos(t/2)),y+5*math.sin(t/2),12.6)
  m2=Vector(x+dx-sign*5*(1-math.cos(t/2)),y+dy-5*math.sin(t/2),12.6)
  return [Edge.make_three_point_arc(p0,m1,pm),Edge.make_three_point_arc(pm,m2,pe)],pe
 def curve(south):
  edges=list(rounded(prefix(south)).edges());e,p=shift(-4,-12,4);edges+=e
  y0=17.435-2*math.sqrt(75)
  edges.append(Edge.make_line(p,Vector(0,y0,12.6)))
  e,p=shift(0,y0,5);edges+=e;e,p=shift(5,p.Y,-5);edges+=e
  assert (p-Vector(*end)).length<1e-7
  return Wire(edges)
 lo,hi=-5.,50.
 assert curve(lo).length<170<curve(hi).length,(curve(lo).length,curve(hi).length)
 for _ in range(45):
  mid=(lo+hi)/2
  if curve(mid).length<170:lo=mid
  else:hi=mid
 south=(lo+hi)/2;path=curve(south)
 s=sweep(Face(Wire.make_circle(1,Plane(origin=Vector(*start),z_dir=(0,1,0)))),path=path)
 return s,dict(waypoints_mm=prefix(south),connected_length_mm=path.length,minimum_bend_radius_mm=5,diameter_mm=2,south_turn_y_mm=south,volume_mm3=s.volume,analytic_volume_mm3=170*math.pi,definition='One continuous cable. R5 filleted prefix followed by three R5 two-arc S shifts (dx=4,5,-5), original mating endpoints.',path_samples_mm=[[v.X,v.Y,v.Z] for v in path.positions([i/2000 for i in range(2001)])])

def run(pitch,inv):
 print('Reading',pitch,flush=True)
 d=read(D037/f'{pitch}mm/dimensions.json');d232=read(BASE/f'{pitch}mm/dimensions.json')
 items=dict(leaves(import_step(BASE/f'{pitch}mm/assembly.step')))
 main=Polygon(d['boards']['main']);outline=Polygon(read(D037/f'{pitch}mm/outline-check.json')['outer_xy_mm'])
 from native_curves import configure
 configure({k:Polygon(v) for k,v in read(HERE.parent/f'issue-198-final/{pitch}mm/dimensions.json')['boards'].items()})
 fixed={n:s for n,s in items.items() if not n.startswith(('GH-','EZmate-170mm','Main-envelope-','cap-gauge-','switch-envelope-','USB-reference-'))}
 # Replace inherited 5/7 mm reservations by source-derived, conservative native-XY budgets.
 components={}
 for c in read(REV4/'main-native-obstacles.json'):
  r=c['ref'];h=inv[r]['study_height_mm']
  g=shape(c['geometry']).buffer(.5,join_style=2) # Explicit XY body allowance over native footprint bbox.
  if h>0:components['Main-study-'+r]=prism(g,11.2,h)
 fixed.update(components)
 slabs={}
 for name,g,z,h in [('under_main',main,2,8),('above_main',main,11.2,3.5),('above_main_to_plane',main,11.2,5),('neck',box(-10.498,-43,10.498,2.267949).intersection(outline),2,12.7)]:
  slab=prism(g,z,h);gross=slab.volume;cuts=[]
  for n,s in fixed.items():
   v=volume(slab,s)
   if v>1e-6:
    cuts.append(dict(part=n,intersection_mm3=v));slab=slab.cut(s)
  slabs[name]=dict(gross_mm3=gross,free_mm3=slab.volume,removed_mm3=gross-slab.volume,z_range_mm=[z,z+h],plan_area_mm2=g.area,subtractions=cuts)
  print(pitch,name,slabs[name]['free_mm3'],flush=True)
 # Outline only. A 1.5-thick numerical occupancy probe is NOT a released cover.
 decks=unary_union([Polygon(p['blank_outline_xy_mm']) for p in d232['plates']])
 service=unary_union([main.buffer(2,join_style=2),Polygon([(-12,-100),(12,-100),(12,-18),(0,0),(-12,-18)])])
 central=outline.buffer(-1.2,join_style=2).intersection(service.buffer(-.2,join_style=2))
 center=[p for p in (list(central.geoms) if hasattr(central,'geoms') else [central]) if p.intersects(main)]
 assert len(center)==1
 cover=center[0]
 # USB overmold upper surface is Z16.32. Avoid its full 30mm travel, with 0.20 XY margin.
 usb=items['USB-reference-overmold'];ub=bounds(usb);keepout=box(ub['min'][0]-.2,ub['min'][1]-30,ub['max'][0]+.2,ub['max'][1]+.2)
 cover=cover.difference(keepout)
 probe=prism(cover,14.7,1.5)
 collisions=[dict(part=n,overlap_mm3=volume(probe,s)) for n,s in fixed.items() if volume(probe,s)>1e-6]
 # Old routes prove why simply fitting a lid fails; their obsolete endpoints are not GH dimensions.
 old_routes={n:dict(**bounds(s),lid_intersection_mm3=volume(probe,s)) for n,s in items.items() if n.startswith('GH-bundle') or n=='EZmate-170mm-route'}
 fly,fd=trial_fly(d)
 flygaps=[]
 for n,s in fixed.items():
  if n in ('EZmate-Fly-plug','EZmate-Main-plug','Main-study-J4') or n.startswith('Fly-official-67'):continue
  gap=fly.distance_to(s)
  if gap<.3:flygaps.append(dict(part=n,gap_mm=gap,overlap_mm3=volume(fly,s)))
 fd.update(top_z_mm=bounds(fly)['max'][2],obstacles_with_gap_below_point3_mm=flygaps,lid_gap_mm=fly.distance_to(probe),passed=not flygaps)
 # Check 170mm route is one solid, analytic length/volume agree. Pass flag also needs obstacles.
 assert len(fly.solids())==1 and fly.is_valid and abs(fd['connected_length_mm']-170)<1e-7
 assert abs(fly.volume-math.pi*170)<1e-4
 usbresults=[]
 from build123d import Axis
 # Exact swept insertion solids: each shell/overmold cross section translates along -Y.
 # Extrusion of all faces along translation vector is a continuous union (convex envelope
 # is conservative here); source USB tools are used for original 30mm sweep separately.
 for n in ('USB-reference-shell','USB-reference-overmold','USB-reference-cable-exit'):
  s=items[n];b=bounds(s)
  envelope=prism(box(b['min'][0],b['min'][1]-30,b['max'][0],b['max'][1]),b['min'][2],b['max'][2]-b['min'][2])
  usbresults.append(dict(part=n,cover_swept_bbox_overlap_mm3=volume(probe,envelope),cover_gap_mm=probe.distance_to(envelope)))
 result=dict(pitch_mm=pitch,verdict='INFEASIBLE',budget=dict(main_top_z=11.2,lid_top_z=16.2,lid_bottom_z=14.7,cover_thickness_mm=1.5,available_above_bare_main_mm=5,available_below_lid_mm=3.5,gh_mated_nominal_top_z=18.5,gh_rigid_shortfall_even_zero_thickness_mm=2.3,gh_rigid_shortfall_to_lid_bottom_mm=3.8,gh_R5_OD1_zero_straight_top_z=24,gh_bend_shortfall_to_lid_bottom_mm=9.3,gh_solder_budget_mm=.2,rack=bounds(items['cable-rack'])),volumes=slabs,cover_outline=mapping(cover),outline_bounds_mm=list(cover.bounds),cover_area_mm2=cover.area,probe_interferences=collisions,old_routes=old_routes,fly_trial=fd,usb_probe=usbresults,retained_usb_limit='D-037 external insertion only; defective official shell/internal mating remains unqualified',channel=read(BASE/f'{pitch}mm/verification.json')['passages'])
 save(OUT/f'{pitch}mm-fly-path.json',fd.pop('path_samples_mm'))
 save(OUT/f'{pitch}mm-measurements.json',result)
 # Save sampled route in reviewable form without exporting a production tree.
 print(pitch,'Fly collisions',flygaps,'cover collisions',collisions,flush=True)
 return result

def main():
 inv=inventory();results=[run(p,inv) for p in (16,17)]
 inputs=set([NATIVE/'inspection/final/main.kicad_pcb',NATIVE/'main-bom.csv',REV4/'main-native-obstacles.json',ROOT/'docs/decisions.md',REV4/'REPORT.md',REV4/'REPORT3.md',BASE/'REPORT.md',BASE/'ASSEMBLY.md'])
 for p in (16,17):
  inputs.update([BASE/f'{p}mm/assembly.step',BASE/f'{p}mm/dimensions.json',BASE/f'{p}mm/verification.json',D037/f'{p}mm/dimensions.json',D037/f'{p}mm/outline-check.json'])
 save(OUT/'inputs-sha256.json',{str(p.relative_to(ROOT)):sha(p) for p in sorted(inputs)})
if __name__=='__main__':main()
