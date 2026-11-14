"""Explicit post-routing rim cleanup, constant-volume topology repair and part assignment."""
from common import *
def run(pitch):
 out=HERE/f'{pitch}mm';idx,raw=cached(pitch);groups={};changes=[]
 for n,k,q in raw:
  if n.startswith('tray-') and q.volume<100:
   b=bounds(q)
   # Only detached upper keyless rim nibs: never floor, PCB support or a random
   # 'keep largest' rule. Larger/out-of-zone fragments remain failed geometry.
   inside=b[0][0]>=-40 and b[1][0]<=40 and b[0][1]>=-10 and b[1][1]<=40 and b[0][2]>=8.5
   if inside:
    changes.append(dict(action='remove detached upper bay rim nib isolated by routing recess',part=n,solid=k,bounds_mm=b,volume_mm3=q.volume));continue
  if n.startswith(('tray-','shell-central','strip-','post-','splice-')) and not q.is_valid:
   fixed=q.fix()
   change=dict(action='OCCT topology repair; no dimensional relaxation',part=n,solid=k,before_valid=False,after_valid=fixed.is_valid,volume_change_mm3=fixed.volume-q.volume)
   if fixed.is_valid and abs(fixed.volume-q.volume)<1e-6:q=fixed
   else:change['accepted']=False
   changes.append(change)
  groups.setdefault(n,[]).append(q)
 central=groups['shell-central']
 if len(central)>1:
  for q in list(central):
   b=bounds(q)
   if q.volume>=100 or b[1][1]>START:continue
   side='left' if (b[0][0]+b[1][0])<0 else 'right';n='strip-'+side
   strip=groups[n][0];gap=strip.distance_to(q)
   merged=strip.fuse(q)
   accepted=gap<1e-6 and merged.is_valid and len(merged.solids())==1 and abs(merged.volume-strip.volume-q.volume)<1e-5
   changes.append(dict(action='assign isolated north-side central wall tongue to adjoining north strip; preserve surface union',part=n,bounds_mm=b,volume_mm3=q.volume,adjacency_gap_mm=gap,accepted=accepted))
   if accepted:groups[n]=[merged];central.remove(q)
 items={n:ss[0] if len(ss)==1 else Compound(children=ss) for n,ss in groups.items()}
 meta=read(out/'measurements.json');meta.pop('status');meta.pop('pitch_mm');meta.pop('parameters');meta['geometry_finish']=changes
 save_geometry(pitch,items,meta);save(out/'geometry-finish.json',dict(status=P['status'],changes=changes))
 print(pitch,'finalized',[(n,len(s.solids()),s.is_valid) for n,s in items.items() if n.startswith(('tray-','strip-','shell-central'))],flush=True)
if __name__=='__main__':run(int(sys.argv[1]))
