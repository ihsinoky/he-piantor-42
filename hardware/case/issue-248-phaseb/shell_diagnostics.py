"""Localize rejected shell exports without changing CAD or repairing meshes."""
from common import *
import struct
from collections import Counter

def run(pitch):
 out=HERE/f'{pitch}mm';base=out/'manufacturing/shell-central-PROVISIONAL'
 q=import_step(base.with_suffix('.step'));solids=list(q.solids())
 data=base.with_suffix('.stl').read_bytes();count=struct.unpack_from('<I',data,80)[0]
 assert len(data)==84+50*count
 edges=Counter()
 for i in range(count):
  row=struct.unpack_from('<12fH',data,84+50*i)
  vertices=[tuple(row[j:j+3]) for j in (3,6,9)]
  for a,b in zip(vertices,vertices[1:]+vertices[:1]):edges[tuple(sorted((a,b)))]+=1
 bad=[dict(endpoints_mm=e,incident_triangles=n) for e,n in edges.items() if n!=2]
 pairs=[dict(solids=[i,j],distance_mm=a.distance_to(b)) for i,a in enumerate(solids) for j,b in enumerate(solids) if i<j]
 save(out/'shell-diagnostics.json',dict(status=P['status'],geometry_sha256=sha(out/'assembly-index.json'),step_sha256=sha(base.with_suffix('.step')),stl_sha256=sha(base.with_suffix('.stl')),solids=[dict(index=i,valid=s.is_valid,volume_mm3=s.volume,bounds_mm=bounds(s)) for i,s in enumerate(solids)],solid_separations=pairs,nonmanifold_edges=bad,verdict='FAIL: exported shell has nonmanifold mesh edges' if bad else 'FAIL: central shell contains disconnected solids' if len(solids)!=1 else 'PASS',qualification='Exact binary STL vertex equality and edge incidence, unchanged from #232 verifier. No welding, dropped material, added bridges or tolerance changes. Distances are kernel results subject to the cap classifier ambiguity.'))
 print(pitch,'shell diagnostic:',len(solids),'solids,',len(bad),'nonmanifold edges',flush=True)

if __name__=='__main__':run(int(sys.argv[1]))
