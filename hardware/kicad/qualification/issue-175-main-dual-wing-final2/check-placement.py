"""Independent position, retained seed and exact axis-aligned pad/SW2 checks."""
from common import *
import pcbnew as p,sexpdata as sx,collections
from shapely.geometry import box,LineString
from shapely.ops import unary_union
src=R/'hardware/kicad/qualification/issue-173-main-dual-wing-final/inputs/final/main.kicad_pcb'
a=p.LoadBoard(str(src));fa={f.GetReference():f for f in a.GetFootprints()}
pose=lambda f:[p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y),f.GetOrientationDegrees()]
def routes(path):return collections.Counter(sx.dumps(x) for x in sx.loads(path.read_text()) if isinstance(x,list) and x and str(x[0]) in ['segment','via'])
def rect(q):
 assert q.GetOrientationDegrees() in [0,180]
 x,y=p.ToMM(q.GetPosition().x),p.ToMM(q.GetPosition().y);w,h=p.ToMM(q.GetSize().x),p.ToMM(q.GetSize().y)
 return box(x-w/2,y-h/2,x+w/2,y+h/2)
rows=[]
for w in sorted((E/'inputs').glob('candidate-*')):
 path=w/'main.kicad_pcb';b=p.LoadBoard(str(path));fb={f.GetReference():f for f in b.GetFootprints()}
 changed={r:dict(before=pose(fa[r]),after=pose(fb[r])) for r in fa if pose(fa[r])!=pose(fb[r])};assert set(changed)=={'C26'}
 assert routes(src)==routes(path)
 for ref,v in json.loads((E/'circuit-intent.json').read_text())['original'].items():assert pose(fb[ref])==[v['x'],v['y'],v['angle']]
 caps=unary_union([rect(q) for q in fb['C26'].Pads()]);sw=unary_union([LineString([(p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y)),(p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y))]).buffer(p.ToMM(t.GetWidth())/2,quad_segs=512) for t in b.GetTracks() if not isinstance(t,p.PCB_VIA) and t.GetNetname()=='SW2' and t.GetLayer()==p.F_Cu])
 j3=unary_union([rect(q) for q in fb['J3'].Pads() if q.GetNumber()=='15']);c27=unary_union([rect(q) for q in fb['C27'].Pads()])
 rows.append(dict(candidate=w.name,changed_footprints=changed,other_65_positions_and_angles_unchanged=True,original_53_fixed=True,seed_copper_canonical_identical=True,C26_SW2_gap_mm=caps.distance(sw),C26_SW2_overlap_mm2=caps.intersection(sw).area,C26_J3_15_gap_mm=caps.distance(j3),C26_J3_15_overlap_mm2=caps.intersection(j3).area,C26_C27_pad_gap_mm=caps.distance(c27),C26_C27_pad_overlap_mm2=caps.intersection(c27).area,board_sha256=digest(path)))
chosen=json.loads((E/'candidate-selection.json').read_text())['selected'];row=next(x for x in rows if x['candidate']==chosen)
assert row['C26_SW2_gap_mm']>=.1 and row['C26_J3_15_gap_mm']>=.1 and row['C26_C27_pad_gap_mm']>=.1
save(E/'placement-check.json',dict(utc=now(),candidates=rows,selected=chosen,pass_selected_geometry=True))
print(json.dumps(rows,indent=2))
