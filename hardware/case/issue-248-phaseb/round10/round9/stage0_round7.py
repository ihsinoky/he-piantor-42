"""Cheap Round-7 evidence. No conductor sweeps or new solids.

Global-X rank is explicitly distinguished from tangent-oriented ribbon rank.
Equal X is broken by Z, then physical cavity number, and ties are disclosed.
"""
import json,math,hashlib,itertools
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def inv(a,b):
 ranks={n:j for j,n in enumerate(b)}
 return sum(ranks[x]>ranks[y] for j,x in enumerate(a) for y in a[j+1:])
def inversion():
 r=read(H/'round5/routes-round5.json');pm=read(H/'round5/pinmap-round5.json');m=read(H/'round5/17mm/measurements.json');result=[]
 for side,sgn in [('left',-1),('right',1)]:
  ws=[w for w in pm['wires'] if w['side']==side];st=[]
  for name,part,k in [('outlet','before',0),('corridor','before',3),('reserve_in','before',4),('reserve_out','after',0),('rise_base','after',2),('rise_top','after',3),('fan','after',4),('Main_row','after',6)]:
   coords={w['wire']:[sgn*x,y,z] for w in ws for x,y,z in [r[part][14-w['wire'] if sgn<0 else w['wire']-1][k]]}
   if name in ('outlet','Main_row'):
    key='wing_endpoint_mm' if name=='outlet' else 'main_endpoint_mm'
    assert all(max(abs(a-b) for a,b in zip(coords[w['wire']],w[key]))<1e-9 for w in ws)
   order=sorted(coords,key=lambda i:(round(coords[i][0],8),round(coords[i][2],8),i))
   ties=[[i for i in order if abs(coords[i][0]-x)<1e-8] for x in sorted({round(v[0],8) for v in coords.values()})];ties=[v for v in ties if len(v)>1]
   st.append(dict(stage=name,order_increasing_global_X_then_Z=order,tied_X_groups=ties,coordinates_mm=coords,inversions_from_previous=inv(st[-1]['order_increasing_global_X_then_Z'],order) if st else 0))
  w=next(v for v in m['wings'] if v['side']==side)
  # Independent dense centreline screen; Euclidean segment-segment minima are
  # computed elsewhere for candidate acceptance, this is only sampled baseline.
  import numpy as np
  from scipy.spatial import cKDTree
  ss=[np.array(v) for v in w['conductor_samples_mm']];near=[]
  for i,j in itertools.combinations(range(14),2):
   distances,indices=cKDTree(ss[j]).query(ss[i]);k=int(distances.argmin())
   if distances[k]<1:near.append(dict(a=i+1,b=j+1,sampled_distance_mm=float(distances[k]),sample_a=k,sample_b=int(indices[k]),point_a_mm=ss[i][k].tolist(),point_b_mm=ss[j][indices[k]].tolist()))
  endinv=inv(st[0]['order_increasing_global_X_then_Z'],st[-1]['order_increasing_global_X_then_Z'])
  result.append(dict(side=side,stages=st,endpoint_X_inversions=endinv,pure_global_X_reversal=endinv==91,endpoint_tangent_note='Wing outlet tangent +Y; Main final tangent differs by side. X ranking is a declared projection, not a topological obstruction. Native Main u increases with pin on both J2/J3, while global X decreases with pin on both; using u as X incorrectly implies reversal.',sampled_pairs_below_OD1=near))
 return result

def length_screen():
 b=read(H/'round5/17mm/length-fly.json');rows=[]
 # Constant angular rate is an optimistic helix: abrupt start/end rate has
 # not been blended. No complete path or bend pass is claimed by this screen.
 for width,n in [('full',14),('half',7)]:
  for L in [12.727,15,20,25,30]:
   rr=[]
   for w in b['conductors']:
    for d in w['all_conductors']:
     i=d['conductor']-1;offset=(i-(n-1)/2)*1.05 if n==14 else ((i%7)-3)*1.05
     excess=math.hypot(L,math.pi*offset)-L;rad=abs(offset)
     R=(rad*rad+(L/math.pi)**2)/rad if rad else None
     rr.append(dict(side=w['side'],pin=i+1,radius_from_twist_axis_mm=rad,helix_length_mm=L+excess,added_length_mm=excess,finished_estimate_mm=d['finished_upper_mm']+excess,curvature_radius_mm=R))
   rows.append(dict(scheme=width,axial_run_mm=L,per_strand=rr,longest_finished_estimate_mm=max(x['finished_estimate_mm'] for x in rr),all_finished_at_most_200=all(x['finished_estimate_mm']<=200 for x in rr),minimum_helical_radius_mm=min(x['curvature_radius_mm'] for x in rr if x['curvature_radius_mm'] is not None),qualifier='Replace equal-length axial segment only; transitions/group exchange excluded. Not a full routing proof.'))
 return dict(tails=read(H/'tail-source.json'),helix_screens=rows,radial_nesting=dict(pitch_mm=1.05,radial_spread_mm=13*1.05,outer_minus_inner_half_turn_mm=math.pi*13*1.05,minimum_inner_radius_mm=5,outer_radius_mm=5+13*1.05,qualifier='43 mm differential alone is not a cap proof: shorter wires may take outer radii. Actual per-pin complete length required.'),split_permutation=dict(independent_half_flips=list(range(7,0,-1))+list(range(14,7,-1)),required_full_flip=list(range(14,0,-1)),remaining_cross_group_inversions=49))

def envelope(pitch):
 # Existing fixed BReps only. Zero-thickness circular faces screen cross-sections;
 # these necessary conditions do not certify an entire swept station.
 import sys
 sys.path.insert(0,str(H));from common import loadbrep,Face,Wire,Plane,Vector
 idx=read(H/f'round5/{pitch}mm/assembly-index.json');found=read(ROOT/'.issue248-runtime/round7/frozen-operands.json')
 bodies=[]
 import numpy as np
 for r in idx:
  if r['name'].startswith(('Wire-','USB-reference-')):continue
  bb=np.array(r['bounds'])
  if bb[1,0]<-20 or bb[0,0]>20 or bb[1,1]<-27 or bb[0,1]>-3:continue
  bodies.append((r,loadbrep(ROOT/found[r['sha256']])))
 results=[]
 candidates=[('round5_postreserve_rise',sgn*x,y,z,(0,11,6.4)) for sgn in (-1,1) for x in (5.25,) for y,z in [(-16,5.8),(-12.5,7.3),(-9,9.2)]]
 candidates += [('upstream_low_leg',sgn*x,y,z,(0,1,0)) for sgn in (-1,1) for x in (5,10.85) for y in (-22,-12,-7) for z in (5.8,)]
 for name,x,y,z,axis in candidates:
  for scheme,radius in [('full',7.325),('half',3.65)]:
   disk=Face(Wire.make_circle(radius,Plane(origin=(x,y,z),z_dir=axis)));bb=np.array([[x-radius,y-radius,z-radius],[x+radius,y+radius,z+radius]])
   hits=[];minimum=1e9
   for r,q in bodies:
    qb=np.array(r['bounds'])
    if np.any(qb[1]<bb[0]) or np.any(qb[0]>bb[1]):continue
    dist=q.distance_to(disk);minimum=min(minimum,dist)
    if dist<1e-7:hits.append(r['name'])
   results.append(dict(station_class=name,center_mm=[x,y,z],axis=axis,scheme=scheme,diameter_mm=radius*2,blocked_cross_section=bool(hits),intersecting_fixed_bodies=hits,minimum_distance_mm=minimum if minimum<1e9 else None,upstream_of_reserve=name=='upstream_low_leg'))
  save(ROOT/'.issue248-runtime/round7'/f'envelope-{pitch}-progress.json',results)
  print(pitch,'crosssections',len(results),'last',results[-1],flush=True)
 save(H/f'stage0-envelope-{pitch}.json',dict(pitch_mm=pitch,round5_index_sha256=sha(H/f'round5/{pitch}mm/assembly-index.json'),method='Exact distance from existing fixed solids to circular zero-thickness station cross-sections. No new solids or strands. Necessary cross-section test only, not continuous station acceptance.',cross_sections=results))
 print(pitch,'envelopes done',sum(not r['blocked_cross_section'] for r in results),'/',len(results),flush=True)

if __name__=='__main__':
 import sys
 if len(sys.argv)>1:envelope(int(sys.argv[1]))
 else:
  save(H/'stage0-round7.json',dict(round5_routes_sha256=sha(H/'round5/routes-round5.json'),pinmap_sha256=sha(H/'round5/pinmap-round5.json'),rank_convention='increasing global X; ties within 1e-8 sorted by Z then pin; tied groups disclosed; stages listed in actual route traversal (reserve precedes rise in round5)',inversion_analysis=inversion(),analytic_length=length_screen()))
  print('Inversion and analytic length evidence written; no solids generated')
