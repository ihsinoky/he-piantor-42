"""Open routing passages in underside ribs, while retaining every required roof skin."""
from common import *
def run(pitch):
 out=HERE/f'{pitch}mm';idx,raw=cached(pitch);meta=read(out/'measurements.json')
 regions={r['properties']['name']:shape(r['geometry']) for r in read(out/'surface-plan.geojson')['features']};blisters=meta['blisters'];allowed=[]
 for n,g in regions.items():
  exceptions=unary_union([shape(b['outer']) for b in blisters]) if n in ('plateau','slope','low_south') else Polygon()
  base=g.difference(exceptions)
  if base.is_empty:continue
  a,m=(TOP+M*START,M) if n=='slope' else (PLATE,0) if n=='low_south' else (TOP,0)
  vertical_skin=2*math.sqrt(1+m*m)
  allowed+=sloped(base,a-vertical_skin,m,100)
 for b in blisters:allowed.append(prism(shape(b['outer']),-40,b['top_z_mm']-2+40))
 allowed=Compound(children=allowed)
 projected=[];zmin=100;zmax=-100
 for wing in meta['wings']:
  for pts in wing['conductor_samples_mm']:
   projected.append(LineString([(x,y) for x,y,z in pts]).simplify(.005).buffer(.87,quad_segs=16))
   zmin=min(zmin,min(p[2] for p in pts)-.87);zmax=max(zmax,max(p[2] for p in pts)+.87)
 g=clean(unary_union(projected));tool=prism(g,zmin,zmax-zmin)
 clipped=tool.intersect(allowed)
 assert clipped is not None
 cutter=Compound(children=list(clipped));items={};changes=[]
 for name,k,q in raw:
  if name in ('shell-central','strip-left','strip-right'):
   before=q.volume;s=q.cut(cutter);blocked=None
   detached=[]
   if len(s.solids())>1:
    retained=[]
    for piece in s.solids():
     # Only remove a detached underside rib if exact subtraction proves it
     # contains no material outside the independent below-skin allowed volume.
     protected=piece.cut(allowed)
     if abs(protected.volume)<1e-7:
      detached.append(dict(bounds_mm=bounds(piece),volume_mm3=piece.volume,protected_material_mm3=abs(protected.volume)))
     else:retained.append(piece)
    if len(retained)!=1:
     blocked=dict(reason='proposed passage disconnects required-skin-bearing pieces; original part preserved',skin_bearing_components=len(retained))
     s=q;detached=[]
    else:s=retained[0]
   assert s.is_valid and len(s.solids())==1,(name,s.is_valid,len(s.solids()))
   changes.append(dict(part=name,removed_volume_mm3=before-s.volume,detached_underside_ribs=detached,blocked_passage=blocked,valid=s.is_valid,solids=len(s.solids())))
   q=s
  assert name not in items
  items[name]=q
 for k in ('status','pitch_mm','parameters'):meta.pop(k,None)
 meta['round4_inner_wall_routing_passages']=dict(changes=changes,projection=mapping(g),height_interval_mm=[zmin,zmax],clearance_radius_mm=.87,method='Conservative fitted route projection over its full height interval, clipped strictly below the exact normal 2mm required roof and blister cap undersides; only printed shell underside ribs are removed. No required roof skin, plate, board, POM or tray is cut here.')
 save_geometry(pitch,items,meta);save(out/'inner-wall-passages.json',dict(geometry_sha256=sha(out/'assembly-index.json'),**meta['round4_inner_wall_routing_passages']))
 print(pitch,'inner wall routing passages',changes,flush=True)
if __name__=='__main__':run(int(sys.argv[1]))
