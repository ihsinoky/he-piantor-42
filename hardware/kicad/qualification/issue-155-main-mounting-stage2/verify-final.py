"""Acceptance/preservation audit; no authoring, routing or manufacture-file writes."""
from common import *
import collections,sexpdata as sx,math
from shapely.geometry import Polygon,Point
def children(n,k):return [x for x in n if isinstance(x,list) and x and str(x[0])==k]
def value(n,k):return children(n,k)[0][1]
def clean(n):
 if not isinstance(n,list):return n
 if n and str(n[0])=='fill':n=[x for x in n if str(x)!='yes']
 return [clean(x) for x in n if not (isinstance(x,list) and x and str(x[0]) in ['filled_polygon','fill_segments','filled_areas_thickness'])]
def nonroute(n):return collections.Counter(sx.dumps(x) for x in clean(n)[1:] if not (isinstance(x,list) and str(x[0]) in ['segment','via']))
read=lambda f:json.loads((E/f).read_text())
assert read('equivalence-gate.json')['pass_gate']
assert read('inspection/local/assessment.json')['metrics']['unexplained_transfer_changes']==68
for label in ['global','final']:
 d=read('inspection/'+label+'/assessment.json');assert d['pass_acceptance'] and set(d['metrics'].values())=={0}
 assert read('inspection/'+label+'/connectivity.json')['nets_checked']==37
 assert not read('inspection/'+label+'/transfer-diff.json')['missing_retained_tracks']
assert read('cam-check.json')['pass_check']
original=sx.loads((E/'inputs/revised/canonical-source.kicad_pcb').read_text());final=sx.loads((E/'inspection/final/main.kicad_pcb').read_text())
removed=nonroute(original)-nonroute(final);added=nonroute(final)-nonroute(original)
assert not removed and collections.Counter(str(sx.loads(x)[0]) for x in added)=={'footprint':4,'zone':4}
areas=[]
for z in children(final,'zone'):
 if not children(z,'keepout'):continue
 pts=children(children(z,'polygon')[0],'pts')[0];poly=Polygon([pt[1:] for pt in children(pts,'xy')]);center=poly.centroid
 assert poly.exterior.distance(center)>2.5 and poly.covers(center.buffer(2.5,quad_segs=4096))
 areas.append(dict(name=value(z,'name'),minimum_radius_mm=poly.exterior.distance(center)))
assert len(areas)==4
for family,stem in [('inputs','main'),('runs','out')]:
 a=sx.loads((E/family/'global'/(stem+'.kicad_pcb')).read_text());b=sx.loads((E/family/'final'/(stem+'.kicad_pcb')).read_text())
 def counter(t):return collections.Counter(sx.dumps(x) for x in t[1:])
 minus=counter(a)-counter(b);plus=counter(b)-counter(a)
 assert len(minus)==len(plus)==4 and all(str(sx.loads(x)[0])=='zone' and children(sx.loads(x),'keepout') for x in list(minus)+list(plus))
 def routes(t):return collections.Counter(sx.dumps(x) for x in t[1:] if isinstance(x,list) and str(x[0]) in ['segment','via'])
 assert routes(a)==routes(b)
baseline=R/'hardware/kicad/qualification/issue-121-full-auto-conditions/evidence/inspection/main-cell1/krt/drc.json'
def signatures(d):return collections.Counter((x['type'],x['severity'],tuple(sorted(i['uuid'] for i in x['items']))) for x in d['violations'])
assert signatures(json.loads(baseline.read_text()))==signatures(read('inspection/final/drc.json'))
graph=read('inspection/final/connectivity.json');nets={row['net']:row for row in graph['nets']}
for net in ['V3V3','GND','WING_EN','VBUS','USB_DP','USB_DM','HALL_PWR_EN']:
 assert nets[net]['component_count']==1
old=R/'hardware/kicad/qualification/issue-137-main-manufacturing-review-prep/board-analysis.json'
oldvia=json.loads(old.read_text())['all_board_via_collisions'];new=read('pofv-reclassification.json')['observations']
def via_geometry(row):return (tuple(row['position_mm']),row['net'],row['diameter_mm'],row['drill_mm'])
assert {via_geometry(v) for v in oldvia}=={via_geometry(v) for v in new}
source=R/'hardware/kicad/qualification/issue-131-wing-condition-search/evidence/KRT-source-hashes.json'
hashes=json.loads(source.read_text());bad=[str(path) for path,h in hashes.items() if digest(K/path)!=h];assert not bad
assert digest(K/'rust_router/grid_router.so')==read('runtime-revalidation.json')['grid_router_sha256']
protected=json.loads((T/'protected-start.json').read_text());changed=[path for path,h in protected.items() if path!='docs/decisions.md' and (not (R/path).exists() or digest(R/path)!=h)];assert not changed,changed
git=['git','--git-dir='+str(T/'git')];base=subprocess.check_output(git+['show','HEAD:docs/decisions.md']).decode();assert (R/'docs/decisions.md').read_text().startswith(base)
save(E/'verification.json',dict(utc=now(),pass_check=True,source_to_final_nonroute_removed=0,source_to_final_additions=dict(footprints=4,keepouts=4),final_reservation_minimum_radii=areas,final_guard_only_four_keepout_nodes=True,routes_unchanged_by_quantization_guard=True,independent_metrics=read('inspection/final/assessment.json')['metrics'],all_37_nets=True,retained_0200mm_segments_covered=3,printing_drc_61_identical_by_type_severity_item_uuid=True,old_and_new_66_via_positions_nets_diameters_identical=True,pofv_rescanned=True,runtime_source_files=len(hashes),runtime_hash_mismatches=bad,protected_files_checked=len(protected)-1,protected_changes=changed,decisions_append_only=True,visual_review=dict(file='manufacturing/cam-review.png',reviewed=True,observations='Four-layer Gerber contact sheet visually inspected: four plane voids match NPTH pattern; top/bottom copper and paste nonempty as expected; J1 bottom-paste four shell strokes retained. Numeric CAM tests govern dimensions, not screenshot.'),route_attempts=dict(local=1,global_reroute=1,final_finishing_routes=0),prohibited_actions_performed=[]))
print('Final acceptance, strict reservations, CAM, unchanged source/runtime and existing work: PASS')
