"""Round 3 plate-boundary ownership, seam steps, and required-skin material audit."""
from common import *
from build import plan,legacy_plan
from certified_distance import boundary_distance

def lines(g):
 if g.is_empty:return []
 if g.geom_type in ('LineString','LinearRing'):return [g]
 return [p for c in getattr(g,'geoms',[]) for p in lines(c)]

def run(pitch):
 out=HERE/f'{pitch}mm';idx,raw=cached(pitch);meta=read(out/'measurements.json')
 d,keys,regions,decks,cover=plan(pitch);_,_,old,_,_=legacy_plan(pitch)
 plates=unary_union([Polygon(p['blank_outline_xy_mm']) for p in d['plates']])
 central=unary_union([regions[n] for n in ('plateau','slope','low_south')])
 oldcentral=unary_union([old[n] for n in ('plateau','slope','low_south')])
 exterior=[dict(area_mm2=g.area,bounds_mm=list(g.bounds),geometry=mapping(g),reason='separate outer south perimeter rim, outside the declared central bay component containing (0,20); no area/volume ranking') for g in polygons(oldcentral.difference(plates)) if not g.covers(Point(0,20))]
 mask=prism(plates,-20,70);shells=[(n,k,q) for n,k,q in raw if n in ('shell-central','strip-left','strip-right')]
 material=[]
 for n,k,q in shells:
  print(pitch,'seam ownership',n,k,flush=True)
  material.append(dict(part=n,solid=k,plate_silhouette_overlap_mm3=volume(q,mask)))
 contacts=[]
 for n,k,q in shells:
  for pn,pk,plate in raw:
   if pn not in ('plate-left','plate-right'):continue
   print(pitch,'seam boundary',n,pn,flush=True)
   dist,proof=boundary_distance(q,plate,zero_precision_mm=1e-6)
   contacts.append(dict(shell=n,shell_solid=k,plate=pn,common_mm3=volume(q,plate),minimum_boundary_gap_mm=dist,minimum_boundary_gap_interval_mm=proof['minimum_distance_interval_mm'],distance_proof=proof))
 actual={r['properties']['name']:shape(r['geometry']) for r in read(out/'surface-plan.geojson')['features']}
 blisters=meta['blisters'];seams=[];required=[]
 # Use the exact authorized CAD openings, not inscribed polygon approximations.
 holes=[cylinder(x,y,2.55,-1,40) for x,y in P['south_opening_xy_mm']]
 holes += [cylinder(x,-30,r,TOP-d,h) for x in (-8,8) for r,d,h in [(1.1,3,5),(2,1,2)]]
 for n,g in actual.items():
  # Diagnostic boundary matching only; the 1e-7 buffer never edits geometry.
  seam=g.boundary.intersection(plates.boundary.buffer(1e-7,join_style=2))
  if not seam.is_empty:
   pts=[xy for line in lines(seam) for xy in line.coords]
   if pts:
    def top(x,y):
     z=TOP+M*(START-y) if n=='slope' else PLATE if n=='low_south' else TOP
     for b in blisters:
      if shape(b['outer']).buffer(1e-8).covers(Point(x,y)):z=max(z,b['top_z_mm'])
     return z
    # Include all blister boundary intersections to capture changes in height.
    for b in blisters:
     cross=seam.intersection(shape(b['outer']).boundary)
     for p in getattr(cross,'geoms',[cross]):
      if p.geom_type=='Point':pts.append(tuple(p.coords[0]))
    steps=[top(x,y)-PLATE for x,y in pts]
    seams.append(dict(region=n,length_mm=seam.length,geometry=mapping(seam),nominal_horizontal_gap_mm=0.,nominal_horizontal_overlap_mm=0.,shell_minus_plate_top_step_range_mm=[min(steps),max(steps)],plate_top_z_mm=PLATE,plate_bottom_z_mm=PLATE-1.5,matching_tolerance_mm=1e-7))
  exceptions=unary_union([shape(b['outer']) for b in blisters]) if n in ('plateau','slope','low_south') else Polygon()
  base=g.difference(exceptions)
  if not base.is_empty:
   a,m=(TOP+M*START,M) if n=='slope' else (PLATE,0) if n=='low_south' else (TOP,0)
   print(pitch,'required skin',n,flush=True)
   roof=fuseall(sloped(base,a,m))
   if n in ('plateau','slope','low_south'):roof=roof.cut(*holes)
   common=sum(volume(roof,q) for sn,sk,q in shells)
   required.append(dict(region=n,required_volume_mm3=roof.volume,actual_common_mm3=common,missing_required_skin_mm3=max(0,roof.volume-common),normal_thickness_mm=2.))
 for b in blisters:
  print(pitch,'blister skin',b['name'],flush=True)
  g=shape(b['outer']);top=b['top_z_mm'];roof=prism(g,top-2,2).cut(*holes)
  common=sum(volume(roof,q) for sn,sk,q in shells)
  required.append(dict(region=b['name']+' blister cap',required_volume_mm3=roof.volume,actual_common_mm3=common,missing_required_skin_mm3=max(0,roof.volume-common),normal_thickness_mm=2.))
 save(out/'seam.json',dict(status=P['status'],geometry_sha256=sha(out/'assembly-index.json'),rule='Shell ownership ends at full aluminium blank silhouette, including apertures. Central ownership is the component containing bay datum (0,20); external south perimeter rim is outside that footprint. North strips obey the same silhouette boundary. No bridge over a key well.',plate_boundary_source='unchanged #232 dimensions.json blank_outline_xy_mm, not deck_outline and not aperture edges',out_of_ownership_fragments=exterior,removed_plate_owned_area_mm2=oldcentral.intersection(plates).area,retained_central_footprint_area_mm2=central.area,seams=seams,shell_plate_contacts=contacts,ownership_material=material,required_skin=required,authorized_skin_void_method='Exact CAD cylinders: south radius2.55 through; north radius1.1 through and radius2 counterbore only at top1mm. No polygon hole approximation and no blanket radius2 roof exception.',ownership_passed=all(r['plate_silhouette_overlap_mm3']<1e-6 for r in material),skin_passed=all(r['missing_required_skin_mm3']<1e-6 for r in required),plate_contact_passed=all(r['common_mm3']<1e-6 for r in contacts)))
 print(pitch,'ownership',max(r['plate_silhouette_overlap_mm3'] for r in material),'skin missing',max(r['missing_required_skin_mm3'] for r in required),'central solids',sum(n=='shell-central' for n,k,q in shells),flush=True)
if __name__=='__main__':run(int(sys.argv[1]))
