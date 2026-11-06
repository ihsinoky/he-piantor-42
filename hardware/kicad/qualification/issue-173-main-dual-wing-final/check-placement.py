"""Independent placement, unchanged seed copper, and local clearance readback."""
from common import *
import pcbnew as p,sexpdata as sx,collections
from shapely.geometry import box,LineString
from shapely.ops import unary_union
old=R/'hardware/kicad/qualification/issue-169-main-dual-wing-followup/inputs/seed-b/main.kicad_pcb'
new=E/'inputs/final/main.kicad_pcb'
a=p.LoadBoard(str(old));b=p.LoadBoard(str(new))
fa={f.GetReference():f for f in a.GetFootprints()};fb={f.GetReference():f for f in b.GetFootprints()}
assert fa.keys()==fb.keys()
def pose(f):return [p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y),f.GetOrientationDegrees()]
changed={r:dict(before=pose(fa[r]),after=pose(fb[r])) for r in fa if pose(fa[r])!=pose(fb[r])}
assert set(changed)=={'C26'}
def children(n,k):return [x for x in n if isinstance(x,list) and x and str(x[0])==k]
def canonical_routes(path):
 ast=sx.loads(path.read_text());return collections.Counter(sx.dumps(x) for k in ['segment','via'] for x in children(ast,k))
assert canonical_routes(old)==canonical_routes(new)
f=fb['C26'];assert f.GetOrientationDegrees()==0
def rectangle(pad):
 x,y=p.ToMM(pad.GetPosition().x),p.ToMM(pad.GetPosition().y);w,h=p.ToMM(pad.GetSize().x),p.ToMM(pad.GetSize().y)
 return box(x-w/2,y-h/2,x+w/2,y+h/2)
caps=unary_union([rectangle(q) for q in f.Pads()])
switch=unary_union([LineString([(p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y)),(p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y))]).buffer(p.ToMM(t.GetWidth())/2,quad_segs=512) for t in b.GetTracks() if not isinstance(t,p.PCB_VIA) and t.GetNetname()=='SW2' and t.GetLayer()==p.F_Cu])
distance=caps.distance(switch);assert distance>=.1
# Exact pad-to-pad overlap independently confirms the native DRC blocker.
j3=next(q for q in fb['J3'].Pads() if q.GetNumber()=='15');assert fb['J3'].GetOrientationDegrees()==0
overlap=rectangle(next(q for q in f.Pads() if q.GetNumber()=='2')).intersection(rectangle(j3)).area
assert overlap>0
save(E/'placement-check.json',dict(utc=now(),pass_existing_placement_and_seed_integrity=True,changed_footprints=changed,footprints_compared=len(fa),other_65_positions_and_angles_unchanged=True,all_seed_segments_and_vias_byte_canonical_identical=True,C26_to_SW2_seed_min_copper_gap_mm=distance,C26_pad2_to_J3_pad15_overlap_mm2=overlap,overall_preflight_pass=False,candidate_board_sha256=digest(new)))
print('Only C26 moved; all seed copper retained; SW2 clear; J3 overlap confirmed',distance,overlap)
