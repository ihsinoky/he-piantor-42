"""Preserve the complete source floor band before remaking splice pilots."""
from common import *
def run(pitch):
 idx,raw=cached(pitch);groups={}
 for n,k,q in raw:groups.setdefault(n,[]).append(q)
 old=source(pitch);changes=[]
 for side in ('left','right'):
  n='tray-'+side;q=fuseall(groups[n]);floor=old[n].intersect(prism(box(-300,-200,300,200),0,2))
  if floor is not None:
   f=Compound(children=list(floor));before=q.volume;q=q.fuse(f)
   changes.append(dict(part=n,restored_floor_volume_mm3=q.volume-before,top_z_mm=2))
  groups[n]=list(q.solids())
 meta=read(HERE/f'{pitch}mm/measurements.json')
 for k in ('status','pitch_mm','parameters'):meta.pop(k,None)
 meta['floor_restoration']=changes
 save_geometry(pitch,{n:ss[0] if len(ss)==1 else Compound(children=ss) for n,ss in groups.items()},meta)
 print(pitch,'floor restoration',changes,flush=True)
if __name__=='__main__':run(int(sys.argv[1]))
