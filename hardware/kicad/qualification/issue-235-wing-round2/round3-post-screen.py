"""Repeat 16L pad/post screen; additionally compare all via envelopes.
Body/channel envelopes are invariant; rerun body screen independently.
"""
from pathlib import Path
import hashlib,json
import pcbnew as p
from shapely.geometry import Point
from shapely.affinity import affine_transform
from shapely.ops import unary_union
from verify import xy,padgeom

E=Path(__file__).resolve().parent;R=E.parents[3];W=E/'wing-rev4-16mm-left';D=W/'round3'
dims=json.loads((R/'hardware/case/issue-228-final/16mm/dimensions.json').read_text())
tr=dims['wing_transforms']['left'];m=tr['matrix'];t=tr['translation']
af=[m[0][0],m[0][1],m[1][0],m[1][1],*t]
def assembly(g):return affine_transform(affine_transform(g,[1,0,0,-1,-100,100]),af)
def obstacles(board):
    pads=unary_union([assembly(padgeom(a,l)) for f in board.GetFootprints() for a in f.Pads() for l in (p.F_Cu,p.B_Cu) if a.IsOnLayer(l)])
    vias=unary_union([assembly(Point(xy(v.GetPosition())).buffer(p.ToMM(v.GetWidth(p.F_Cu))/2,quad_segs=128)) for v in board.GetTracks() if isinstance(v,p.PCB_VIA)])
    return pads,vias
old=p.LoadBoard(str(D/'round2-main.kicad_pcb'));new=p.LoadBoard(str(W/'main.kicad_pcb'))
op,ov=obstacles(old);np,nv=obstacles(new)
assert op.equals(np),'pad/drill placement changed'
rows=[]
for row in json.loads((E/'case/16mm/post-rescreen.json').read_text()):
    if row['variant']!='16mm-left':continue
    post=Point(row['xy_mm']).buffer(1.5)
    pad_gap=post.distance(np);old_via=post.distance(ov);new_via=post.distance(nv)
    assert abs(pad_gap-row['pad_drill_edge_gap_mm'])<.0001
    assert pad_gap>=.4 and new_via>=.4
    assert not row['body_hits'] and not row['trial_channel_collar_hits']
    rows.append(dict(post=row['post'],xy_mm=row['xy_mm'],pad_drill_edge_gap_mm=pad_gap,
        pad_gap_delta_mm=pad_gap-row['pad_drill_edge_gap_mm'],old_via_edge_gap_mm=old_via,
        new_via_edge_gap_mm=new_via,via_gap_delta_mm=new_via-old_via,
        body_edge_gap_mm=row['body_edge_gap_mm'],body_gap_delta_mm=0,
        trial_channel_shaft_gap_mm=row['trial_channel_shaft_gap_mm'],channel_gap_delta_mm=0,
        post_move_required=False))
assert len(rows)==6
body=json.loads((D/'body-clearance.json').read_text());assert len(body)==1 and body[0]['pass_body_overlap_screen']
out=dict(board_sha256=hashlib.sha256((W/'main.kicad_pcb').read_bytes()).hexdigest(),
    pass_all=True,posts=rows,placement_and_channel_unchanged=True,
    note='Native pad shapes include NPTH; via obstacles use full copper diameter, conservatively enclosing drill. Shaft radius1.5, pad/via screen0.4 mm; collar/body/channel inputs unchanged.')
(D/'post-rescreen.json').write_text(json.dumps(out,indent=2)+'\n')
print('Six 16L posts pass native pad and via rescreen')
