"""Nominal local dimensions and actual fitted distances, with no inherited PASS."""
from common import *
from certified_distance import boundary_distance
def run(pitch):
 out=HERE/f'{pitch}mm';idx,raw=cached(pitch)
 roof=[s for n,k,s in raw if n=='shell-central'];rows=[]
 for n,k,s in raw:
  if not n.startswith(('Main-GH-','cover-screw-','cover-Main-spacer-')):continue
  gap,proof=min((boundary_distance(q,s) for q in roof),key=lambda r:r[0])
  rows.append(dict(part=n,distance_mm=gap,roof_witness_mm=proof['a_point_mm'],part_witness_mm=proof['b_point_mm'],boundary_distance_proof=proof,common_mm3=sum(volume(q,s) for q in roof)))
 save(out/'local-measures.json',dict(status=P['status'],geometry_sha256=sha(out/'assembly-index.json'),dimensions=P,results=rows,note='GH uses B1 nominal drawing bounds. Exact trimmed-face distances bypass the whole-solid classifier; no allowance relaxed.'))
if __name__=='__main__':run(int(sys.argv[1]))
