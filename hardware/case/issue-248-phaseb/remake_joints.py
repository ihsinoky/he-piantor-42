"""Reuse #246 X0/15 splice relocation, with floor-rooted bosses for the lower stack."""
from common import *
def run(pitch):
 out=HERE/f'{pitch}mm';d=read(out/'measurements.json');idx,raw=cached(pitch)
 if d.get('splice_relocations'):return
 groups={}
 for n,k,q in raw:groups.setdefault(n,[]).append(q)
 changes=[]
 for row,y in [(1,-8),(2,55)]:
  for oldx,newx in [(-5,0),(12,15)]:
   key=f'joint-screw-{row}-{float(oldx):.1f}'.replace('.','_')
   groups[key]=[groups[key][0].translate((newx-oldx,0,0))]
   q=groups[f'splice-{row}'][0].cut(cylinder(newx,y,1.1,-3.01,4.22))
   groups[f'splice-{row}']=[q]
   changes.append(dict(row=row,old_xy_mm=[oldx,y],new_xy_mm=[newx,y],boss_top_z_mm=5.5,pilot_od_mm=1.7))
 for side in ('left','right'):
  n='tray-'+side;q=fuseall(groups[n])
  for y in (-8,55):
   for oldx in (-5,12):q=q.cut(cylinder(oldx,y,3.5,2,6))
   for x in (0,15):
    if (x<3.5)!=(side=='left'):continue
    q=q.fuse(cylinder(x,y,3.5,1.2,4.3)).cut(cylinder(x,y,.85,-.01,5.52))
  # Preserve the final route clearance through the new boss exteriors.
  for w in d['wings']:
   for pts,samples in zip(w['conductor_waypoints_mm'],w['conductor_samples_mm']):
    # Only low sections near the bosses; no unrelated full-height relief here.
    for j in range(len(pts)-1):
     a,b=pts[j:j+2]
     if min(a[2],b[2])>6.37:continue
     g=LineString([(a[0],a[1]),(b[0],b[1])]).buffer(.87,quad_segs=8)
     z=max(2.,min(a[2],b[2])-.87)
     cut=prism(g,z,max(a[2],b[2])+.87-z)
     if volume(q,cut)>1e-6:q=q.cut(cut)
  groups[n]=list(q.solids())
  print(pitch,n,q.is_valid,len(q.solids()),flush=True)
 items={n:ss[0] if len(ss)==1 else Compound(children=ss) for n,ss in groups.items()}
 for k in ('status','pitch_mm','parameters'):d.pop(k,None)
 d['splice_relocations']=changes
 save_geometry(pitch,items,d)
if __name__=='__main__':run(int(sys.argv[1]))
