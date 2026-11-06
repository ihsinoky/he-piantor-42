"""Bounded via relocation, fixed D-021, no router predicates used for acceptance.

Each site tries at most 200 candidate positions (25 radii x 8 directions).
The original surface and reverse connections are extended to the new via using
full-width straight dogbones. Foreign copper clearance is screened with native
KiCad shapes. Saved results MUST still undergo independent four-metric + via
pad qualification. Failing sites are retained and never claimed as qualified.
"""
from common import *
import pcbnew as p
import sys,math,time,collections
src,out,audit=map(Path,sys.argv[1:]);b=p.LoadBoard(str(src));tick=time.monotonic()
violations=json.loads(audit.read_text())['all_vias'];targets=[x for x in violations if x['clearance_violation']]
pads=[q for f in b.GetFootprints() for q in f.Pads() if q.GetAttribute()!=p.PAD_ATTRIB_NPTH]
xy=lambda v:[p.ToMM(v.x),p.ToMM(v.y)]
tracks=list(b.GetTracks());byid={t.m_Uuid.AsString():t for t in tracks}
# Compact bounding boxes reject only pairs too far apart; exact native shapes decide.
def bounds(shape):
 q=shape.BBox();return q.GetLeft(),q.GetTop(),q.GetRight(),q.GetBottom()
def near(a,z,gap):return a[0]<=z[2]+gap and z[0]<=a[2]+gap and a[1]<=z[3]+gap and z[1]<=a[3]+gap
def inventory(skip):
 rows=[];holes=[]
 for q in pads+list(b.GetTracks()):
  if q==skip:continue
  for l in [p.F_Cu,p.B_Cu]:
   if q.IsOnLayer(l):
    s=q.GetEffectiveShape(l);rows.append((q.GetNetCode(),l,s,bounds(s)))
  if isinstance(q,p.PCB_VIA):
   s=q.GetEffectiveHoleShape();holes.append((q.GetNetCode(),s,bounds(s)))
 return rows,holes
ledger=[]
for site in targets:
 assert time.monotonic()-tick<1800,'local repair time limit'
 v=byid[site['uuid']];old=p.VECTOR2I(v.GetPosition());net=v.GetNetCode();width=p.FromMM(.3 if v.GetNetname() in ['GND','HALL_5V'] else .1)
 obstacles,holes=inventory(v);candidates=[];chosen=None;reject=collections.Counter()
 for step in range(1,26):
  r=step*.1
  for a in range(0,360,45):
   new=p.VECTOR2I(old.x+p.FromMM(r*math.cos(math.radians(a))),old.y+p.FromMM(r*math.sin(math.radians(a))))
   candidates.append(new)
 for new in candidates:
  # All component copper pads, regardless of net or paste status.
  disk=p.SHAPE_CIRCLE(new,p.FromMM(.4));db=bounds(disk)
  if any(near(db,bounds(q.GetEffectiveShape(p.F_Cu)),0) and q.GetEffectiveShape(p.F_Cu).Collide(disk) for q in pads):reject['pad_gap']+=1;continue
  v.SetPosition(new);shapes=[];bridges=[]
  for l in [p.F_Cu,p.B_Cu]:
   shapes.append((l,v.GetEffectiveShape(l)))
   t=p.PCB_TRACK(b);t.SetStart(old);t.SetEnd(new);t.SetWidth(width);t.SetLayer(l);t.SetNetCode(net);bridges.append(t);shapes.append((l,t.GetEffectiveShape(l)))
  hit=False
  for l,s in shapes:
   sb=bounds(s)
   if any(n!=net and layer==l and near(sb,bb,p.FromMM(.1)) and s.Collide(z,p.FromMM(.1)) for n,layer,z,bb in obstacles):hit=True;break
   if any(n!=net and near(sb,bb,p.FromMM(.2)) and s.Collide(z,p.FromMM(.2)) for n,z,bb in holes):hit=True;break
  if hit:reject['foreign_copper_or_hole']+=1;v.SetPosition(old);continue
  hole=v.GetEffectiveHoleShape();hb=bounds(hole)
  if any(near(hb,bb,p.FromMM(.2)) and hole.Collide(z,p.FromMM(.2)) for n,z,bb in holes):reject['hole_to_hole']+=1;v.SetPosition(old);continue
  chosen=new
  for t in bridges:b.Add(t)
  break
 v.SetPosition(chosen if chosen is not None else old)
 ledger.append(dict(uuid=site['uuid'],net=v.GetNetname(),old_mm=xy(old),new_mm=None if chosen is None else xy(chosen),candidates_tested=sum(reject.values())+(chosen is not None),rejections=dict(reject),bridge_width_mm=p.ToMM(width),bridges_added=2 if chosen is not None else 0))
 print(site['uuid'],v.GetNetname(),xy(old),'->',None if chosen is None else xy(chosen),dict(reject),flush=True)
out.parent.mkdir(parents=True,exist_ok=True);p.SaveBoard(str(out),b)
save(out.with_suffix('.repair.json'),dict(utc=now(),source_sha256=digest(src),output_sha256=digest(out),candidate_bound_per_site=200,time_bound_seconds=1800,elapsed_seconds=time.monotonic()-tick,sites=len(targets),repaired=sum(x['new_mm'] is not None for x in ledger),unrepaired=sum(x['new_mm'] is None for x in ledger),ledger=ledger))
