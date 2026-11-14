"""Rebuild the south left splice boss with fresh analytic cylindrical topology."""
from common import *
def run(pitch):
 out=HERE/f'{pitch}mm';idx,raw=cached(pitch);items={n:q for n,k,q in raw};q=items['tray-left']
 # Preserve complete parent audit for unchanged-operand pair replay.
 oldhash=sha(out/'assembly-index.json')
 if (out/'audit.json').exists() and read(out/'audit.json').get('geometry_sha256')==oldhash:
  folder=out/'evidence';folder.mkdir(exist_ok=True)
  ip=folder/(oldhash[:12]+'-pre-splice-index.json');ap=folder/(oldhash[:12]+'-pre-splice-audit.json')
  save(ip,idx);save(ap,read(out/'audit.json'))
  save(out/'E-boss-audit-parent.json',dict(index_file=str(ip.relative_to(out)),audit_file=str(ap.relative_to(out)),geometry_sha256=oldhash))
 # Rebuild the boss/floor junction inside an explicit 8x8 mm local box.
 # The narrow annular cleanup left near-coincident trims at Z2. Replace
 # that junction and restore the exact native floor patch through Z2.
 # This is case-only geometry removal above Z1.8; no mesh vertices are welded.
 mask=prism(box(-4,51,4,59),1.8,4)
 floor=source(pitch)['tray-left'].intersect(prism(box(-4,51,4,59),1.6,.4))
 assert floor is not None
 fresh=cylinder(0,55,3.5,1.6,3.9).fuse(Compound(children=list(floor)))
 s=q.cut(mask).fuse(fresh).cut(cylinder(0,55,.85,-.01,5.52))
 assert s.is_valid and len(s.solids())==1
 probe=RUN/f'tray-boss-{pitch}-roundtrip.step';export_step(s,probe);reload=import_step(probe)
 assert reload.is_valid and len(reload.solids())==1
 record=dict(part='tray-left',feature='X0/Y55 south splice boss',boss_od_mm=7.,pilot_od_mm=1.7,boss_top_z_mm=5.5,cleanup_xy_bounds_mm=[-4,51,4,59],cleanup_z_mm=[1.8,5.8],floor_overlap_mm=.4,source_floor_top_rebuilt_mm=.2,before_volume_mm3=q.volume,after_volume_mm3=s.volume,volume_change_mm3=s.volume-q.volume,source_valid=s.is_valid,reloaded_step_valid=reload.is_valid,reloaded_step_solids=len(reload.solids()),roundtrip_volume_delta_mm3=reload.volume-s.volume)
 items['tray-left']=s;d=read(out/'measurements.json')
 for k in ('status','pitch_mm','parameters'):d.pop(k,None)
 d['round5_splice_boss_rebuild']=record;save_geometry(pitch,items,d)
 save(out/'splice-boss-rebuild.json',dict(geometry_sha256=sha(out/'assembly-index.json'),**record));print(pitch,record,flush=True)
if __name__=='__main__':run(int(sys.argv[1]))
