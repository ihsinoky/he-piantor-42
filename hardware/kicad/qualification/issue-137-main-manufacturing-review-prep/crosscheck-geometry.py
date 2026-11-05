"""Independent stdlib circle/rectangle/capsule math vs the native KiCad result.

Run from repo root after analyze-board.py; JSON on stdout, no design writes.
This checks the logged geometry, not manufacturing tolerance or solderability.
"""
import collections
import json
import math
from pathlib import Path
import re

BASE=Path('hardware/kicad/qualification/issue-137-main-manufacturing-review-prep')
native=json.loads((BASE/'board-analysis.json').read_text())
pcb=next(p for p in native['inputs'] if p.endswith('.kicad_pcb'))
def parse(path):
    stack=[]; root=None
    for t in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',Path(path).read_text()):
        if t=='(':
            node=[]
            if stack: stack[-1].append(node)
            else: root=node
            stack.append(node)
        elif t==')': stack.pop()
        else: stack[-1].append(json.loads(t) if t.startswith('"') else t)
    assert not stack
    return root
def children(a,k): return [v for v in a if isinstance(v,list) and v and v[0]==k]
def child(a,k): return children(a,k)[0]
def rotate(x,y,deg):
    a=math.radians(deg)
    return x*math.cos(a)+y*math.sin(a), -x*math.sin(a)+y*math.cos(a)
root=parse(pcb); pads=[]
for fp in children(root,'footprint'):
    props={p[1]:p[2] for p in children(fp,'property')}; at=child(fp,'at')
    fx,fy=map(float,at[1:3]); fa=float(at[3]) if len(at)>3 else 0
    for p in children(fp,'pad'):
        if p[2]=='np_thru_hole': continue
        at=child(p,'at'); px,py=rotate(*map(float,at[1:3]),fa)
        angle=float(at[3]) if len(at)>3 else 0
        pads.append(dict(ref=props['Reference'],pad=p[1],uuid=child(p,'uuid')[1],
            shape=p[3],x=fx+px,y=fy+py,angle=angle,w=float(child(p,'size')[1]),h=float(child(p,'size')[2])))
def distance(x,y,p):
    x,y=rotate(x-p['x'],y-p['y'],-p['angle'])
    w,h=p['w'],p['h']
    if p['shape']=='rect': return math.hypot(max(abs(x)-w/2,0),max(abs(y)-h/2,0))
    if p['shape']=='circle':
        assert abs(w-h)<1e-9
        return max(0,math.hypot(x,y)-w/2)
    if p['shape']=='oval':
        radius=min(w,h)/2
        return max(0,math.hypot(max(abs(x)-max(w-h,0)/2,0),max(abs(y)-max(h-w,0)/2,0))-radius)
    raise AssertionError(p['shape'])
graphics=[]
for g in children(root,'gr_circle'):
    if child(g,'layer')[1]!='F.Paste': continue
    assert child(g,'fill')[1]=='yes' and float(child(child(g,'stroke'),'width')[1])==0
    x,y=map(float,child(g,'center')[1:3]);ex,ey=map(float,child(g,'end')[1:3])
    diameter=2*math.dist((x,y),(ex,ey))
    graphics.append(dict(ref='',pad='',uuid=child(g,'uuid')[1],shape='circle',x=x,y=y,angle=0,w=diameter,h=diameter))
for g in children(root,'gr_rect'):
    if child(g,'layer')[1]!='F.Paste': continue
    assert child(g,'fill')[1]=='yes' and float(child(child(g,'stroke'),'width')[1])==0
    x1,y1=map(float,child(g,'start')[1:3]);x2,y2=map(float,child(g,'end')[1:3])
    graphics.append(dict(ref='',pad='',uuid=child(g,'uuid')[1],shape='rect',x=(x1+x2)/2,y=(y1+y2)/2,angle=0,w=abs(x2-x1),h=abs(y2-y1)))
rows=[]
for row in native['observations']:
    x,y=row['position_mm']; radius=row['diameter_mm']/2; drill=row['drill_mm']/2
    hits=[p for p in pads if distance(x,y,p)<radius-1e-9]
    assert {p['uuid'] for p in hits}=={p['uuid'] for p in row['copper_pad_hits']}
    for p in hits:
        n=next(q for q in row['copper_pad_hits'] if q['uuid']==p['uuid'])
        assert math.dist(n['position_mm'],[p['x'],p['y']])<1e-6
        assert n['via_center_in_pad']==(distance(x,y,p)<1e-9)
        assert n['drill_overlaps_pad']==(distance(x,y,p)<drill-1e-9)
    ghits=[g for g in graphics if distance(x,y,g)<radius-1e-9]
    assert {g['uuid'] for g in ghits}=={g['uuid'] for g in row['paste_graphic_hits']}, (row['log_index'], [(g['uuid'],distance(x,y,g)) for g in ghits],row['paste_graphic_hits'])
    for g in ghits:
        n=next(q for q in row['paste_graphic_hits'] if q['uuid']==g['uuid'])
        assert n['drill_overlaps_graphic']==(distance(x,y,g)<drill-1e-9)
    p=hits[0];d=distance(x,y,p)
    rows.append(dict(log_index=row['log_index'], ref=p['ref'],pad=p['pad'],
        center_to_pad_boundary_outside_mm=round(d,6),drill_intrusion_mm=round(drill-d,6),
        via_disk_intrusion_mm=round(radius-d,6),
        center_in_pad=d<1e-9,drill_overlaps_pad=d<drill-1e-9,
        paste_graphics=len(ghits),drill_overlaps_paste=any(distance(x,y,g)<drill-1e-9 for g in ghits)))
print(json.dumps(dict(status='pass',checked_observations=len(rows),
    method='Independent S-expression reader; Euclidean disk-to-rect/circle/capsule distances, strict positive overlap, numerical epsilon 1nm. Compared every copper/paste hit UUID, pad position and drill flags with KiCad.',
    rows=rows),indent=2))
