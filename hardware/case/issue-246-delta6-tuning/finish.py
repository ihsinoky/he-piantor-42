"""Exact contact bounds, single-solid exports, and case/cover metrology after audit."""
import sys,json,math,shutil
import study as s
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common,BRepAlgoAPI_Fuse
from build123d import Shape

def reuse_identical_wing(side,idx,out):
 # Only reuse an independently completed union when every placed constituent
 # is byte-identical and the delivered union still matches its recorded hash.
 peer=out.parent/'17mm'
 if out==peer or not (peer/'metrology.json').exists():return None
 pm=s.read(peer/'metrology.json');pi=s.read(peer/'assembly-index.json')
 if pm.get('geometry_index_sha256')!=s.sha(peer/'assembly-index.json'):return None
 def signatures(index):return [(r['name'],r['solid'],r['brep_sha256']) for r in index if r['name'].startswith('Wing-'+side)]
 sig=signatures(idx)
 if sig!=signatures(pi):return None
 m=pm['wings'][side]
 if not m['valid'] or m['solids']!=1 or not all(r['valid'] and r['solids']==1 and r['nondecreasing'] for r in m['merge_checks']):return None
 filename=f'wing-{side}.step'
 if pm['delivered_sha256'][filename]!=s.sha(peer/filename):return None
 shutil.copyfile(peer/filename,out/filename)
 result=dict(m,reused_from_pitch_mm=17,identical_constituent_sha256=[v[2] for v in sig],source_geometry_index_sha256=pm['geometry_index_sha256'])
 print('CABLE UNION',side,'reusing byte-identical 17 mm constituents and verified union',flush=True)
 return result

def main(pitch):
 out=s.HERE/f'{pitch}mm';cache=s.RUNTIME/f'audit{pitch}'
 idx=s.read(cache/'index.json');metrology_only='--metrology-only' in sys.argv
 audit=dict(unexpected_interferences=[]) if metrology_only else s.read(out/'audit.json');d=s.read(out/'measurements.json')
 raw=[]
 for i,r in enumerate(idx):
  q=s.TopoDS_Shape();s.BRepTools.Read_s(q,str(cache/f'{i}.brep'),s.BRep_Builder());raw.append(Shape.cast(q))
 contacts=[]
 for r in audit['unexpected_interferences']:
  op=BRepAlgoAPI_Common(raw[r['i']].wrapped,raw[r['j']].wrapped);op.SetRunParallel(True);op.SetUseOBB(True);op.Build()
  assert op.IsDone() and not op.Shape().IsNull()
  q=Shape.cast(op.Shape());contacts.append(dict(**r,overlap_bounds_mm=s.bounds(q)))
 if not metrology_only:s.save(out/'collision-map.json',contacts)
 existing=out/'metrology.json'
 if existing.exists():
  m=s.read(existing)
  if m.get('geometry_index_sha256')==s.sha(cache/'index.json') and all(s.sha(out/n)==v for n,v in m.get('delivered_sha256',{}).items()) and m.get('delivered_sha256'):
   print('METROLOGY reusing index/hash-matched completed measurements',flush=True);return
 # Partition -> one machinable cover. Uniform translation leaves all pocket depths fixed.
 cp=s.shape(d['cover_outline']);cover=s.prism(cp,14.7,1.5);gs=[]
 for sgn,angle in [(-1,-120),(1,120)]:
  a=math.radians(angle);x=sgn*17.102146;y=42.075
  gs.append(s.Polygon([(x+u*math.cos(a)+v*math.sin(a),y-u*math.sin(a)+v*math.cos(a)) for u,v in [(-10.375,-1.6),(10.375,-1.6),(10.375,5.55),(-10.375,5.55)]]))
 fs=d['fly']['path_samples_mm']
 for g,z in [(s.unary_union(gs).buffer(.3),15.95),(s.LineString([(p[0],p[1]) for p in fs]).simplify(.02).buffer(1.22,quad_segs=8),15.8),(s.box(-5,-55,5,-45),15.2)]:
  cover=cover.cut(s.prism(cp.intersection(g),14.699,z-14.699))
 for x,y in d['retention_sites_mm']:
  cover=cover.cut(s.cylinder(x,y,1.1,14.699,1.502)).cut(s.Solid.make_cone(.8,2.1,1,s.Plane(origin=(x,y,15.2))))
 cover=cover.translate((0,0,s.DELTA))
 pv=sum(q.volume for r,q in zip(idx,raw) if r['name']=='Cover')
 assert cover.is_valid and len(cover.solids())==1 and abs(cover.volume-pv)<1e-3
 s.export_step(cover,out/'cover-study.step')
 met=dict(cover=dict(valid=True,solids=1,partition_volume_mm3=pv,volume_mm3=cover.volume,volume_difference_mm3=abs(cover.volume-pv),bounds_mm=s.bounds(cover)),wings={},printing={})
 for side in ('left','right'):
  reused=reuse_identical_wing(side,idx,out)
  if reused:met['wings'][side]=reused
  else:
   parts=[q for r,q in zip(idx,raw) if r['name'].startswith('Wing-'+side)]
   # Conservative fanout constituents are audited separately; delivered cable is their union.
   # Start from the shared lower envelope, then fuse each continuous wire.
   # Validate every merge and reject mass loss, including apparently valid
   # but corrupted OCCT results. No fuzzy tolerance changes are used.
   rows=[(r,q) for r,q in zip(idx,raw) if r['name'].startswith('Wing-'+side)]
   cable=next(q for r,q in rows if r['name'].endswith('-lower'))
   merges=[]
   wire_rows=[(r,q) for r,q in rows if not r['name'].endswith('-lower')]
   # Deterministic side-specific order avoids OCCT tangent-merge failures.
   # All merges use exact Fuse, with validity, connectedness and mass checks.
   if side=='left':wire_rows.reverse()
   for r,q in wire_rows:
    before=cable.volume
    op=BRepAlgoAPI_Fuse(cable.wrapped,q.wrapped);op.Build()
    assert op.IsDone() and not op.Shape().IsNull()
    cable=Shape.cast(op.Shape())
    merges.append(dict(solid=r['solid'],valid=cable.is_valid,solids=len(cable.solids()),volume_mm3=cable.volume,volume_before_mm3=before,nondecreasing=cable.volume>=before-1e-4))
    print('CABLE UNION',side,merges[-1],flush=True)
   union_ok=all(r['valid'] and r['solids']==1 and r['nondecreasing'] for r in merges)
   met['wings'][side]=dict(valid=cable.is_valid and union_ok,solids=len(cable.solids()),volume_mm3=cable.volume,merge_checks=merges)
   # A rejected candidate may also fail cable-union topology. Preserve that
   # diagnostic and the original audited envelope instead of losing metrology.
   if cable.is_valid and len(cable.solids())==1:
    s.export_step(cable,out/f'wing-{side}.step')
  tray=[q for r,q in zip(idx,raw) if r['name']=='tray-'+side]
  assert tray
  tray=s.Compound(children=tray)
  b=tray.bounding_box()
  met['printing'][side]=dict(with_5mm_brim_xy_mm=[b.size.X+10,b.size.Y+10],z_mm=b.size.Z,within_220x220x250=max(b.size.X+10,b.size.Y+10)<=220 and b.size.Z<=250,valid=tray.is_valid,solids=len(tray.solids()),constituents=[dict(volume_mm3=q.volume,bounds_mm=s.bounds(q)) for q in tray.solids()])
 met['geometry_index_sha256']=s.sha(cache/'index.json')
 met['delivered_sha256']={n:s.sha(out/n) for n in ('cover-study.step','wing-left.step','wing-right.step')}
 s.save(out/'metrology.json',met)
 print('METROLOGY',s.DELTA,pitch,met,flush=True)
if __name__=='__main__':main(int(sys.argv[1]))
