"""Apply normal-roof blend allowance to pre-checkpoint geometry without a full rebuild."""
from common import *
from build import gh
def run(pitch):
 out=HERE/f'{pitch}mm';d=read(out/'measurements.json');idx,raw=cached(pitch)
 if all(b.get('north_blend_extension_mm')==.5 for b in d['blisters']):return
 groups={}
 for n,k,q in raw:groups.setdefault(n,[]).append(q)
 q=fuseall(groups['shell-central'])
 footprint=unary_union([shape(f['geometry']) for f in read(out/'surface-plan.geojson')['features'] if f['properties']['name'] in ('plateau','slope','low_south')])
 fs=d['fly']['path_samples_mm']
 for b in d['blisters']:
  n=b['name'];ceil=b['ceiling_z_mm'];top=b['top_z_mm']
  g=gh('left' if n=='GH-left' else 'right')[1] if n.startswith('GH') else LineString([(x,y) for x,y,z in fs]).simplify(.003).buffer(1.003,quad_segs=16)
  outer=clean(g.buffer(2.30,join_style=2).intersection(footprint).intersection(box(-300,START+(TOP-top)/M-.5,300,300)))
  q=q.fuse(prism(outer,PLATE-2,top-(PLATE-2)))
  q=q.cut(prism(clean(shape(b['cavity']).intersection(outer)),-10,ceil+10))
  b.update(outer=mapping(outer),north_blend_extension_mm=.5)
 before=q.volume;fixed=q.fix()
 if fixed.is_valid and abs(fixed.volume-before)<1e-6:q=fixed
 groups['shell-central']=list(q.solids())
 items={n:ss[0] if len(ss)==1 else Compound(children=ss) for n,ss in groups.items()}
 for k in ('status','pitch_mm','parameters'):d.pop(k,None)
 d['geometry_finish'].append(dict(action='extend blister blend 0.50 mm north under existing slope; external plane and ceiling/top dimensions retained',valid=q.is_valid,solids=len(q.solids())))
 save_geometry(pitch,items,d)
 print(pitch,'blend',q.is_valid,len(q.solids()),flush=True)
if __name__=='__main__':run(int(sys.argv[1]))
