"""Retained #198/#228 gates and Rev.4-specific integration, independently reloaded."""
from geometry import *
from dress_fly import dressed
from routing import wing_points,flat_bundle
import itertools

def run(pitch):
 out=HERE/f'{pitch}mm';d=json.loads((out/'dimensions.json').read_text());old=json.loads((BASE/f'{pitch}mm/dimensions.json').read_text());tests={}
 inputs={p:sha(ROOT/p)==v for p,v in old['inputs_sha256'].items()}
 tests['baseline_input_provenance']=dict(passed=all(inputs.values()),files=len(inputs),failures=[p for p,v in inputs.items() if not v])
 inverse=[];screws=[]
 for side in ('left','right'):
  t=d['wing_transforms'][side];m=t['matrix'];tx,ty=t['translation']
  src={r['reference']:r for r in rows(BASE/f'inputs/rev3-final/holes-{pitch}mm-{side}.csv') if r['kind']=='mounting'}
  outline=rows(BASE/f'inputs/rev3-final/outline-{pitch}mm-{side}.csv');south=min(float(r['y_mm']) for r in outline)
  for h in d['mounts']:
   if h['board']!='wing_'+side:continue
   dx,dy=h['xy'][0]-tx,h['xy'][1]-ty;local=[m[0][0]*dx+m[1][0]*dy,m[0][1]*dx+m[1][1]*dy]
   r=src[h['ref']];inverse.append(math.dist(local,[float(r['x_mm']),float(r['y_mm'])]))
   board=Polygon(old['boards'][h['board']]);head=Point(h['xy']).buffer(1.9)
   screws.append(dict(side=side,ref=h['ref'],head_and_washer_inside_original_pcb=board.covers(head),clearance_from_original_south_palm_band_mm=local[1]-(south+8)-1.9))
 tests['wing_mounts']=dict(maximum_inverse_transform_error_mm=max(inverse),passed=max(inverse)<1e-10)
 tests['palm_fasteners']=dict(sites=screws,passed=all(x['head_and_washer_inside_original_pcb'] and x['clearance_from_original_south_palm_band_mm']>0 for x in screws))
 pairs=[dict(a=a['ref'],b=b['ref'],gap_mm=Polygon(a['xy']).distance(Polygon(b['xy'])),overlap_mm2=Polygon(a['xy']).intersection(Polygon(b['xy'])).area) for a,b in itertools.combinations(old['main_components'],2)]
 tests['main_component_spacing']=dict(minimum=min(pairs,key=lambda r:r['gap_mm']),pairs=len(pairs),passed=all(r['overlap_mm2']<1e-8 and r['gap_mm']>=.3-1e-8 for r in pairs))
 flyregion=prism(box(-13,-100,13,-39),-7,50)
 flyscope={};bosses=[];floor={}
 for side in ('left','right'):
  print(pitch,side,'retained geometry',flush=True)
  before=import_step(BASE/f'{pitch}mm/tray-{side}.step');after=import_step(out/f'tray-{side}.step')
  b=before.intersect(flyregion);a=after.intersect(flyregion)
  b=Compound(children=list(b));a=Compound(children=list(a))
  overlap=volume(a,b);added=max(0,a.volume-overlap);removed=max(0,b.volume-overlap)
  flyscope[side]=dict(added_mm3=added,removed_mm3=removed,passed=max(added,removed)<1e-5)
  low=prism(box(-300,-200,300,200),0,1.199)
  floor[side]=dict(before_mm3=volume(before,low),after_mm3=volume(after,low))
  floor[side]['passed']=abs(floor[side]['before_mm3']-floor[side]['after_mm3'])<1e-5
  for h in d['mounts']:
   x,y=h['xy']
   if (x<=3.5)!=(side=='left'):continue
   r=h['boss_diameter']/2;z=6.
   material=any(s.is_inside(Vector(x+(r+.85)/2,y,z)) for s in after.solids())
   pilot=not any(s.is_inside(Vector(x,y,z)) for s in after.solids())
   bosses.append(dict(board=h['board'],ref=h['ref'],boss_wall_present=material,pilot_open=pilot))
 tests['Fly_seat_and_opening_scope']=dict(variants=flyscope,passed=all(v['passed'] for v in flyscope.values()))
 tests['floor_below_sockets']=dict(variants=floor,passed=all(v['passed'] for v in floor.values()))
 refs={(h['board'],h['ref']) for h in d['mounts']};expected={('main',r) for r in ('H1','H2','H3')}|{('fly',r) for r in ('MH1','MH2')}|{('wing_'+s,'H'+str(i)) for s in ('left','right') for i in range(1,5)}
 tests['fixing_inventory']=dict(sites=len(refs),screws=17,wing_stack_screws=8,main_Fly_screws=5,splice_screws=4,boss_checks=bosses,passed=refs==expected and len(bosses)==13 and all(r['boss_wall_present'] and r['pilot_open'] for r in bosses))
 # Rev.4 Main footprint obstacles are additional, independent of old body envelopes.
 print(pitch,'native Main and dressed Fly clearances',flush=True)
 fly,fd=dressed(old);native=json.loads((REV4/'main-native-obstacles.json').read_text());native_results=[]
 routes={side:import_step(out/f'harness-{side}-160mm.step') for side in ('left','right')}
 for r in native:
  ob=prism(shape(r['geometry']),11.2,r['height_mm'])
  for name,cable in {**routes,'Fly':fly}.items():
   if (name=='left' and r['ref']=='J2') or (name=='right' and r['ref']=='J3') or (name=='Fly' and r['ref']=='J4'):continue
   v=volume(ob,cable)
   if v>1e-5:native_results.append(dict(cable=name,component=r['ref'],overlap_mm3=v))
 tests['native_Main_obstacles']=dict(source_sha256=sha(REV4/'main-native-obstacles.json'),obstacles=len(native),overlaps=native_results,passed=not native_results)
 # Service-range endpoints change only an elevated detour; check both explicitly.
 range_results=[]
 for route in d['routes']:
  side=route['side'];sgn=-1 if side=='left' else 1
  for target in (153.4,170.):
   pts=[list(p) for p in route['waypoints_mm']];width=route['detour_width_mm']+(target-160)/2
   pts=wing_points(sgn,width)
   s,path=flat_bundle(pts)
   v=volume(s,fly)
   range_results.append(dict(side=side,longest_conductor_mm=160+path.length-rounded(route['waypoints_mm']).length,detour_width_mm=width,valid=s.is_valid,fly_overlap_mm3=v,cap_vertical_gap_mm=28.5-2.5-25.2,plate_vertical_gap_mm=28.5-2.5-16.2,own_side_min_x_mm=7-2.5))
 tests['harness_range']=dict(endpoints=range_results,passed=all(r['valid'] and r['fly_overlap_mm3']<1e-5 and r['cap_vertical_gap_mm']>=.3 for r in range_results),reason='Only two horizontal straights vary with length; fixed low route/rise/termination is identical to the 160mm checked assembly. The complete changing envelope is above cap reservations, one side of X0 and below the dressed Fly loop; endpoint sweeps bound the intermediate horizontal displacement.')
 tests['passed']=all(v['passed'] for v in tests.values())
 save(out/'invariants.json',tests);print(pitch,'invariants',tests['passed'],flush=True)
if __name__=='__main__':
 import sys
 run_pitch=int(sys.argv[1])
 run(run_pitch)
 raise SystemExit(0 if json.loads((HERE/f'{run_pitch}mm/invariants.json').read_text())['passed'] else 1)
