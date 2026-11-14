"""Restore unchanged E support regions removed by tray routing cuts; keep failures visible."""
from common import *
def run(pitch):
 out=HERE/f'{pitch}mm';idx,raw=cached(pitch);original=source(pitch);groups={};changes=[]
 oldhash=sha(out/'assembly-index.json')
 if (out/'audit.json').exists() and read(out/'audit.json').get('geometry_sha256')==oldhash:
  import shutil
  folder=out/'evidence';folder.mkdir(exist_ok=True)
  indexpath=folder/(oldhash[:12]+'-pre-E-index.json');auditpath=folder/(oldhash[:12]+'-pre-E-audit.json')
  save(indexpath,idx);shutil.copyfile(out/'audit.json',auditpath)
  save(out/'E-boss-audit-parent.json',dict(index_file=str(indexpath.relative_to(out)),audit_file=str(auditpath.relative_to(out)),geometry_sha256=oldhash))
 for n,k,q in raw:groups.setdefault(n,[]).append(q)
 for side in ('left','right'):
  n='tray-'+side;q=fuseall(groups[n]);before=q.volume
  for name,ss in groups.items():
   if not name.startswith('plate-screw-'+side+'-'):continue
   b=bounds(ss[0]);x=sum(v[0] for v in b)/2;y=sum(v[1] for v in b)/2
   # Exact source material in a named local support region; retain the original
   # pilots. Apply the same neutral-band removal as the case build.
   local=original[n].intersect(cylinder(x,y,3.5,2,8.00001))
   if local is None:continue
   s=Compound(children=list(local));pieces=[]
   lo=s.intersect(cylinder(x,y,3.5,2,1))
   hi=s.intersect(cylinder(x,y,3.5,5.65,4.35))
   if lo is not None:pieces+=list(lo)
   if hi is not None:pieces += [r.translate((0,0,-2.65)) for r in hi]
   for r in pieces:q=q.fuse(r)
  assert q.is_valid and len(q.solids())==1
  groups[n]=[q];changes.append(dict(part=n,restored_volume_mm3=q.volume-before,region_radius_mm=3.5,z_mm=[2,7.35],reason='Preserve source E bosses and original pilots; wire relief cannot remove thread-bearing material.'))
  # Only these operands are rewritten. All other serialized BReps stay byte-identical.
  ii=next(i for i,r in enumerate(idx) if r['name']==n);assert sum(r['name']==n for r in idx)==1
  path=RUN/f'geometry{pitch}/{ii}.brep';BRepTools.Write_s(q.wrapped,str(path))
  idx[ii].update(bounds=bounds(q),valid=q.is_valid,volume_mm3=q.volume,sha256=sha(path))
 save(RUN/f'geometry{pitch}/index.json',idx);save(out/'assembly-index.json',idx)
 m=read(out/'measurements.json');m['E_boss_restoration']=changes;save(out/'measurements.json',m);save(out/'E-boss-restoration.json',dict(status=P['status'],geometry_sha256=sha(out/'assembly-index.json'),changes=changes))
 print(pitch,changes,flush=True)
if __name__=='__main__':run(int(sys.argv[1]))
