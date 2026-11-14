"""Nominal local dimensions and actual fitted distances, with no inherited PASS."""
from common import *
def run(pitch):
 out=HERE/f'{pitch}mm';idx,raw=cached(pitch)
 roof=[s for n,k,s in raw if n=='shell-central'];rows=[]
 for n,k,s in raw:
  if not n.startswith(('Main-GH-','cover-screw-','cover-Main-spacer-')):continue
  distance=min(q.distance_to_with_closest_points(s) for q in roof)
  rows.append(dict(part=n,distance_mm=distance[0],roof_witness_mm=list(distance[1]),part_witness_mm=list(distance[2]),common_mm3=sum(volume(q,s) for q in roof)))
 save(out/'local-measures.json',dict(status=P['status'],geometry_sha256=sha(out/'assembly-index.json'),dimensions=P,results=rows,note='GH uses B1 nominal drawing bounds. Inspect cap-witnesses.json for 17 mm solid-classifier inconsistency; distance alone is not promoted to release approval.'))
if __name__=='__main__':run(int(sys.argv[1]))
